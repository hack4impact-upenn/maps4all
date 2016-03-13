import unittest
import time
from app import create_app, db
from app.models import Resource, Descriptor, OptionAssociation, TextAssociation


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

    def test_create_resource(self):
        r = Resource(name='test')
        a = OptionAssociation(option=0)
        options = ["True", "False"]
        a.descriptor = Descriptor(name="Open", values=options)
        r.option_descriptors.append(a)

        for option_assoc in r.option_descriptors:
        	print option_assoc.option
        	print option_assoc.descriptor

        db.session.add(r)
        db.session.commit()

    def test_print_random(self):
        Resource.generate_fake()
        Resource.print_users()


        