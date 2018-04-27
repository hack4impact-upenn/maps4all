import time
import unittest

from app import create_app, db
from app.models import Resource, Descriptor, OptionAssociation, TextAssociation


class ResourceModelTestCase(unittest.TestCase):
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
        """Test creating a resource with a single option"""
        r = Resource(name='test')
        a = OptionAssociation(option=0)
        options = ['True', 'False']
        a.descriptor = Descriptor(name='Open', dtype='option', values=options)
        r.option_descriptors.append(a)

        option_assoc = r.option_descriptors[0]
        self.assertEqual(option_assoc.option, 0)
        self.assertEqual(option_assoc.descriptor.name, 'Open')
        self.assertEqual(option_assoc.descriptor.values, options)
