#!/usr/bin/env python3

# SQLAlchemy postgresql connection: https://vsupalov.com/flask-sqlalchemy-postgres/

import os
import requests
import json
import pika, sys
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import psycopg2

from threading import Thread
import time


## EVENT COLLABORATION
def create_rabbitmq_connection():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='34.118.234.233'))
    channel = connection.channel()
    channel.queue_declare(queue='scrape_signal')
    return (connection, channel)
## EVENT COLLABORATION: try to connect to rabbitmq 3 times. Sleep for 5 seconds if not available.
connection = None
channel = None
success = False
for i in range(3):
    try:
        connection, channel = create_rabbitmq_connection()
        success = True
    except:
        time.sleep(5)

    if success:
        break
print(success)

def callback(ch, method, properties, body):
    body = json.loads(body)
    print(body)
    if (body == "scrape signal"):
        requests.get("http://localhost:5050/scrape")
    elif (body == "delete signal"):
        requests.get("http://localhost:5050/delete_records")
    # print("hello world! RabbitMQ consumption working :D Very satisfied with the outcome")

def some_print_func():
    print("hello world! RabbitMQ consumption working :D Very satisfied with the outcome")

if success:
    def rabbit_thread(channel):
        channel.basic_consume(queue='scrape_signal', on_message_callback=callback, auto_ack=True)
        channel.start_consuming()

    t2 = Thread(target=rabbit_thread, args=(channel,))
    t2.start()
    

def someThreadedFunc():
    currTime = time.time()
    totalTime = 0
    print(totalTime)
    while (True):
        if time.time()-currTime >= 3600.0:
            currTime = time.time()
            totalTime += 1
            requests.get("http://127.0.0.1:5050/scrape")
            print(totalTime)

t1 = Thread(target=someThreadedFunc)
t1.start()

print("moving on!")

def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = f"environment variable '{name}' not set."
        raise Exception(message)

POSTGRES_URL = get_env_variable("POSTGRES_URL")
POSTGRES_USER = get_env_variable("POSTGRES_USER")
POSTGRES_PW = get_env_variable("POSTGRES_PW")
POSTGRES_DB = get_env_variable("POSTGRES_DB")
AIC_API = "https://api.artic.edu/api/v1/artworks"
# AIC_IIIF = "https://www.artic.edu/iiif/2/{identifier}/full/843,/0/default.jpg"

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

db = SQLAlchemy(app)

class Artpieces(db.Model):
    __tablename__ = 'artpieces'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    image_id = db.Column(db.Text, nullable = True)
    dimensions_detail = db.Column(db.Text, nullable = True)

def ArtpiecesJson(rows):
    tempList = []
    for i in rows:
        data = { 
            'id': i.id,
            'name': i.name,
            'image_id': i.image_id,
            'dimensions_detail': i.dimensions_detail
        }
        tempList.append(data)
    return json.dumps(tempList)

@app.route("/delete_records", methods=["GET"])
def delete_records():
    print("deleted!")
    artworks = db.session.query(Artpieces).delete()
    db.session.commit()
    return "deleted!"

@app.route("/scrape", methods=["GET"])
def scrape():
    # make an API call to The Art Institute of Chicago
    response = requests.get(AIC_API)
    loaded = json.loads(response.text)
    data = loaded['data']

    for row in data:
        id = row['id']
        name = row['title']
        image_id = row['image_id']
        dimensions_detail = json.dumps(row['dimensions_detail'])

        artpiece = db.session.query(Artpieces).filter_by(id=id).first()
        if artpiece is None:
            new_entry = Artpieces(id=id, name=name, image_id=image_id, dimensions_detail=dimensions_detail)
            db.session.add(new_entry)
            db.session.commit()
            # print("stored!")
        else:
            # print("already exists!")
            pass

    print("data scraped!")
    return "data scraped!"
    # return str(response.status_code) + "<br>" + json.dumps(data)

if __name__ == "__main__":
    print("hello world!")
    app.run(port=5050)
    # test commit
