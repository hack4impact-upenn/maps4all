from .. import db


class Suggestion(db.Model):
    """
    Association between a resource and potential suggestions for it
    """
    __tablename__ = 'suggestions'
    id = db.Column(db.Integer, primary_key=True)
    # suggestion_type is 0 for insertion, 1 for edit, and 2 for deletion: get rid of this
    # timestamp, contact: name, email, number, read/unread
    # front-end notification: read/unread

    suggestion_type = db.Column(db.Integer)
    resource_id = db.Column(db.Integer)
    suggestion_text = db.Column(db.String(150))

    def __repr__(self):
        return '%s: %s' % (self.suggestion_type, self.resource.name)

    @staticmethod
    def generate_fake_inserts(count=20):
        """Generate a number of fake insert suggestions."""
        from sqlalchemy.exc import IntegrityError
        from faker import Faker

        fake = Faker()

        num_words = 10
        for i in range(count):
            s_text = fake.sentence(nb_words=num_words)
            s_insert = Suggestion(suggestion_type=0, resource_id=-1, suggestion_text=s_text)
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
        from models import Resource

        fake = Faker()

        num_words = 10
        for i in range(count):
            r_name = fake.word()
            r = Resource(name=r_name)
            s_text = fake.sentence(nb_words=num_words)
            s_edit = Suggestion(suggestion_type=1, resource_id=r.id, suggestion_text=s_text)

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
        from models import Resource

        fake = Faker()

        num_words = 10
        for i in range(count):
            r_name = fake.word()
            r = Resource(name=r_name)
            s_text = fake.sentence(nb_words=num_words)
            s_delete = Suggestion(suggestion_type=2, resource_id=r.id, suggestion_text=s_text)

            db.session.add(s_delete)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
