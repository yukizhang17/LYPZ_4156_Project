import unittest
import os
import sys
import uuid

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from database_services.sql_service import *

class Test_TestSqlService(unittest.TestCase):
    def setUp(self):
        self.db = SqliteService

    def test_database(self):
        email = uuid.uuid4().hex + "@gmail.com"
        apikey = uuid.uuid4().hex

        SqliteService.insert("application", {"email": email, "api_key": apikey, "verified": 0})

        data = SqliteService.select("application", {"email": email})
        self.assertTrue(len(data) == 1)
        self.assertTrue(data[0][1] == apikey)
        self.assertTrue(data[0][2] == 0)

        SqliteService.update("application", {"verified": 1}, {"email": email})

        data = SqliteService.select("application", {"email": email})
        self.assertFalse(data[0][2] == 0)
        self.assertTrue(data[0][2] == 1)

        self.db.delete("application", {"email": email})

        data = SqliteService.select("application", {"email": email})
        self.assertTrue(len(data) == 0)


if __name__ == '__main__':
    unittest.main()