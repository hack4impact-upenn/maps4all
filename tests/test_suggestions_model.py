from datetime import datetime
import pytz
import unittest

from app import create_app, db
from app.models import Resource, Suggestion
from sqlalchemy.exc import IntegrityError



class SuggestionsModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_insertion_suggestion(self):
        """Test suggestion of an insertion"""
        s_text = "Name: Taco Time \n Address: 123 45th Street"
        s_contact_name = "John Doe"
        s_contact_number = "123-456-7890"
        s_contact_email = "taco@time.com"
        s_timestamp = datetime.now(pytz.timezone('US/Eastern'))
        suggestion = Suggestion(suggestion_text=s_text,
                                read=0, contact_name=s_contact_name, contact_email=s_contact_email,
                                contact_phone_number=s_contact_number, submission_time=s_timestamp)
        db.session.add(suggestion)
        db.session.commit()

        r_in_table = Suggestion.query.filter_by(suggestion_text=s_text).first()
        self.assertTrue(r_in_table is not None)
        self.assertTrue(r_in_table.suggestion_text == s_text)
        self.assertTrue(r_in_table.resource_id is None)
        self.assertTrue(r_in_table.read == 0)
        self.assertTrue(r_in_table.contact_phone_number == s_contact_number)
        self.assertTrue(r_in_table.submission_time is not None)
        self.assertTrue(r_in_table.contact_name == s_contact_name)
        self.assertTrue(r_in_table.contact_email == s_contact_email)

    def test_edit_suggestion(self):
        """Test suggestion of an edit"""
        r = Resource(name='test_edit')
        db.session.add(r)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

        r_added = Resource.query.filter_by(name='test_edit').first()
        s_text = "The phone number of this establishment is incorrect: it should be 212-346-5927"
        s_contact_name = "Anonymous Helper"
        s_contact_email = "anony@mous.com"
        s_contact_number = "000-001-0101"
        s_timestamp = datetime.now(pytz.timezone('US/Eastern'))
        suggestion = Suggestion(resource_id=r_added.id, suggestion_text=s_text,
                                read=1, contact_name=s_contact_name, contact_email=s_contact_email,
                                contact_phone_number=s_contact_number, submission_time=s_timestamp)
        db.session.add(suggestion)
        db.session.commit()

        r_in_table = Suggestion.query.filter_by(suggestion_text=s_text).first()
        self.assertTrue(r_in_table is not None)
        self.assertTrue(r_in_table.suggestion_text == s_text)
        self.assertTrue(r_in_table.resource_id == r_added.id)
        self.assertTrue(r_in_table.read == 1)
        self.assertTrue(r_in_table.contact_phone_number == s_contact_number)
        self.assertTrue(r_in_table.submission_time is not None)
        self.assertTrue(r_in_table.contact_name == s_contact_name)
        self.assertTrue(r_in_table.contact_email == s_contact_email)

