import unittest
import time
from app import create_app, db
from app.models import Resource, Suggestion

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
		s_text = "Name: Taco Time \n Address: 123 45th Street \n Contact: John Doe \n 123-456-7890"
		suggestion = Suggestion(suggestion_type = 0, resource_id = -1, suggestion_text=s_text)
		db.session.add(suggestion)
		db.session.commit()

		r_in_table = Suggestion.query.filter_by(suggestion_type = 0).first()
		self.assertTrue(r_in_table is not None)
		self.assertTrue(r_in_table.suggestion_text == s_text)
		self.assertTrue(r_in_table.suggestion_type == 0)
		self.assertTrue(r_in_table.resource_id == -1)

	def test_edit_suggestion(self):
		"""Test suggestion of an edit"""
		r = Resource(name='test_edit')
		s_text = "The phone number of this establishment is incorrect: it should be 212-346-5927"
		suggestion = Suggestion(suggestion_type = 1, resource_id = r.id, suggestion_text=s_text)
		db.session.add(suggestion)
		db.session.commit()

		r_in_table = Suggestion.query.filter_by(suggestion_type=1).first()
		self.assertTrue(r_in_table is not None)
		self.assertTrue(r_in_table.suggestion_text == s_text)
		self.assertTrue(r_in_table.suggestion_type == 1)
		self.assertTrue(r_in_table.resource_id == r.id)

	def test_delete_suggestion(self):
		"""Test suggestion of a delete"""
		r = Resource(name = 'test_delete')
		s_text = "TThis location closed last month"
		suggestion = Suggestion(suggestion_type = 2, resource_id = r.id, suggestion_text=s_text)
		db.session.add(suggestion)
		db.session.commit()

		r_in_table = Suggestion.query.filter_by(suggestion_type=2).first()
		self.assertTrue(r_in_table is not None)
		self.assertTrue(r_in_table.suggestion_text == s_text)
		self.assertTrue(r_in_table.suggestion_type == 2)
		self.assertTrue(r_in_table.resource_id == r.id)		
