from .. import db
from datetime import datetime
import pytz


class Suggestion(db.Model):
    """
    Association between a resource and potential suggestions for it
    """
    __tablename__ = 'suggestions'
    id = db.Column(db.Integer, primary_key=True)
    # suggestion_type is 0 for insertion, 1 for edit, and 2 for deletion
    suggestion_type = db.Column(db.Integer)
    resource_id = db.Column(db.Integer)
    suggestion_text = db.Column(db.String(150))
    # 0 stands for read, 1 stands for unread
    read = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime)
    contact_name = db.Column(db.String(64))
    contact_email = db.Column(db.String(64), unique=True, index=True)
    contact_number = db.Column(db.String(64))

    def __repr__(self):
        return '%s: %s' % (self.suggestion_type, self.resource_id)

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
            s_insert = Suggestion(suggestion_type=0, resource_id=-1, suggestion_text=s_text,
                                  read=s_read, timestamp=s_timestamp, contact_name=s_contact_name,
                                  contact_email=s_contact_email, contact_number=s_contact_number)
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
            s_edit = Suggestion(suggestion_type=1, resource_id=r_added.id, suggestion_text=s_text,
                                read=s_read, timestamp=s_timestamp, contact_name=s_contact_name,
                                contact_email=s_contact_email, contact_number=s_contact_number)
            db.session.add(s_edit)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def generate_fake_deletions(count=20):
        """Generate a number of fake delete suggestions"""
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
            s_read = 1
            s_timestamp = datetime.now(pytz.timezone('US/Eastern'))
            s_contact_name = fake.word()
            s_contact_email = fake.word() + "@" + fake.word() + ".com"
            s_contact_number = "123-456-7890"
            s_delete = Suggestion(suggestion_type=2, resource_id=r_added.id, suggestion_text=s_text,
                                  read=s_read, timestamp=s_timestamp, contact_name=s_contact_name,
                                  contact_email=s_contact_email, contact_number=s_contact_number)

            db.session.add(s_delete)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
