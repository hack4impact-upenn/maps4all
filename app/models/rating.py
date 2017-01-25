from datetime import datetime
from .. import db


class Rating(db.Model):
	""" Star rating and review """
	__tablename__ = 'ratings'
	id = db.Column(db.Integer, primary_key=True)
	resource_id = db.Column(db.Integer, db.ForeignKey('resources.id', ondelete='CASCADE'))
	rating = db.Column(db.Integer)
	review = db.Column(db.Text)
	submission_time = db.Column(db.DateTime)

	def __repr__(self):
		return '%s: %s' % (self.id, self.resource_id)
