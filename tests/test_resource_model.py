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
        a.descriptor = Descriptor(name='Open', values=options)
        r.option_descriptors.append(a)

        option_assoc = r.option_descriptors[0]
        self.assertEquals(option_assoc.option, 0)
        self.assertEquals(option_assoc.descriptor.name, 'Open')
        self.assertEquals(option_assoc.descriptor.values, options)

    def test_create_descriptors(self):
        """Testing creating descriptors with varying numbers of options"""
        r = Resource(name='test')
        r_2 = Resource(name='test2')
        a_1 = OptionAssociation(option=0)
        a_2 = OptionAssociation(option=2)
        a_3 = OptionAssociation(option=4)
        options_1 = ['Yes', 'No', 'Not Available']
        options_2=[1,2,3,4,5,6,7]
        d_1 = Descriptor(name='WheelchairAccessible', values=options_1)
        d_2 =Descriptor(name='NumberOfDaysOpen', values=options_2)
        a_1.descriptor = d_1
        a_2.descriptor = d_2
        a_3.descriptor = d_2
        r.option_descriptors.append(a_1)
        r.option_descriptors.append(a_2)
        r_2.option_descriptors.append(a_3)

        option_2_assoc = r.option_descriptors[1]
        self.assertEquals(option_2_assoc.resource.name, 'test')
        self.assertEquals(option_2_assoc.option, 2)
        self.assertEquals(option_2_assoc.descriptor.values[option_2_assoc.option], 3)

        option_1_assoc = r.option_descriptors[0]
        self.assertEquals(option_1_assoc.resource.name, 'test')
        self.assertEquals(option_1_assoc.option, 0)
        self.assertEquals(option_1_assoc.descriptor.values[option_1_assoc.option], 'Yes')

        option_3_assoc = r_2.option_descriptors[0]
        self.assertEquals(option_3_assoc.resource.name, 'test2')
        self.assertEquals(option_3_assoc.option, 4)
        self.assertEquals(option_3_assoc.descriptor.values[option_3_assoc.option], 5)





