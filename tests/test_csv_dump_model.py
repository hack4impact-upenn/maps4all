import unittest
from app import create_app, db
from app.models import CsvDump, User


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_foo(self):
        csv = CsvDump()
        u = User(password='password')
        print u
        print csv
        self.assertTrue(True)
