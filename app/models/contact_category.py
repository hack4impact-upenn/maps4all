from .. import db


class ContactCategory(db.Model):
    """
    Schema for the categories of contact forms
    """
    __tablename__ = 'contact_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), index=True)
