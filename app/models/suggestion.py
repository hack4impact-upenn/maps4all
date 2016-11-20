from datetime import datetime
import pytz
from .. import db

class Suggestion(db.Model):
    """
    Association between a resource and potential suggestions for it
    """
    __tablename__ = 'suggestions'
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'))
    suggestion_text = db.Column(db.String(250))
    # 0 stands for read, 1 stands for unread
    read = db.Column(db.Boolean, default=False)
    submission_time = db.Column(db.DateTime)
    contact_name = db.Column(db.String(64))
    contact_email = db.Column(db.String(64))
    contact_phone_number = db.Column(db.String(64))
    resource_name = db.Column(db.String(64))
    resource_address = db.Column(db.String(64))

    def __repr__(self):
        return '%s: %s' % (self.id, self.resource_id)

    @staticmethod
    def generate_fake_inserts(count=20):
        """Generate a number of fake insert suggestions."""
        from sqlalchemy.exc import IntegrityError
        from faker import Faker

        fake = Faker()

        num_words = 10
        for i in range(count):
            s_text = fake.sentence(nb_words=num_words)
            s_read = 1
            s_timestamp = datetime.now(pytz.timezone('US/Eastern'))
            s_contact_name = fake.word()
            s_contact_email = fake.word() + "@" + fake.word() + ".com"
            s_contact_number = "123-456-7890"
            s_resource_name = fake.word()
            s_resource_address = fake.word()
            s_insert = Suggestion(suggestion_text=s_text,
                                  read=s_read, submission_time=s_timestamp, contact_name=s_contact_name,
                                  contact_email=s_contact_email, contact_phone_number=s_contact_number,
                                  resource_name=s_resource_name, resource_address=s_resource_address)
            db.session.add(s_insert)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def generate_fake_edits(count=20):
        """Generate a number of fake edit suggestions"""
        from sqlalchemy.exc import IntegrityError
        from faker import Faker
        from ..models import Resource

        fake = Faker()

        num_words = 10
        for i in range(count):
            r_name = fake.word()
            r = Resource(name=r_name)
            db.session.add(r)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

            r_added = Resource.query.filter_by(name=r_name).first()
            s_text = fake.sentence(nb_words=num_words)
            s_read = 0
            s_timestamp = datetime.now(pytz.timezone('US/Eastern'))
            s_contact_name = fake.word()
            s_contact_email = fake.word() + "@" + fake.word() + ".com"
            s_contact_number = "123-456-7890"
            s_edit = Suggestion(resource_id=r_added.id, suggestion_text=s_text,
                                read=s_read, submission_time=s_timestamp, contact_name=s_contact_name,
                                contact_email=s_contact_email, contact_phone_number=s_contact_number)
            db.session.add(s_edit)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

