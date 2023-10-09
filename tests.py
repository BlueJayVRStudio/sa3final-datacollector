#!/usr/bin/env python3

import unittest
from unittest.mock import MagicMock


class TestExample(unittest.TestCase):
    def test_sometest(self):
        a = 1
        b = 1
        self.assertEqual(a, b)
        


if __name__ == "__main__":
    unittest.main()
    
