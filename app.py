#!/usr/bin/env python3

# SQLAlchemy postgresql connection: https://vsupalov.com/flask-sqlalchemy-postgres/

import os
import requests
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import psycopg2


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

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

db = SQLAlchemy(app)

class Artpieces(db.Model):
    __tablename__ = 'artpieces'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

echoForm = '''
    <p>Enter something here?????</p>
     <form action="/echo_user_input" method="POST">
         <input name="user_input">
         <input type="submit" value="Submit!">
     </form>
     '''

@app.route("/")
def main():
    return echoForm

@app.route("/echo_user_input", methods=["POST"])
def echo_input():
    input_text = request.form.get("user_input", "")
    return "You entered: " + input_text # + "\n" + echoForm

@app.route("/test_string")
def get_some_string():
    return requests.get('https://api.ipify.org').content.decode('utf8')

    return "successfully deployed automatically, just got back from running errands :D. Also this is a new test statement"

@app.route("/retrieve_id", methods=["GET"])
def retrieve_id():
    artworks = db.session.query(Artpieces).filter_by(name='testArtPiece').all()

    id = None
    name = None
    for artwork in artworks:
        print(artwork.id)
        id = artwork.id
        name = artwork.name

    if id == None:
        return "no record found :("

    return str(id) + ", " + str(name)

@app.route("/store_id", methods=["GET"])
def store_id():
    new_entry = Artpieces(id=531, name="testArtPiece")
    db.session.add(new_entry)
    db.session.commit()
    return "stored!"

if __name__ == "__main__":
    print("hello")
    app.run(port=5050)
