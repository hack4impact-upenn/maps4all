from .. import db
from .. models import Rating

class OptionAssociation(db.Model):
    """
    Association between a resource and a descriptor with an index for the
    value of the option.
    """
    __tablename__ = 'option_associations'
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'),
                            primary_key=True)
    descriptor_id = db.Column(db.Integer, db.ForeignKey('descriptors.id'),
                              primary_key=True)
    option = db.Column(db.Integer, primary_key=True)
    resource = db.relationship('Resource',
                               back_populates='option_descriptors')
    descriptor = db.relationship('Descriptor',
                                 back_populates='option_resources')

    def __repr__(self):
        return '%s: %s' % (self.descriptor.name,
                           self.descriptor.values[self.option])


class TextAssociation(db.Model):
    """
    Association between a resource and a descriptor with a text field for the
    value of the descriptor.
    """
    __tablename__ = 'text_associations'
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'),
                            primary_key=True)
    descriptor_id = db.Column(db.Integer, db.ForeignKey('descriptors.id'),
                              primary_key=True)
    text = db.Column(db.Text)
    resource = db.relationship('Resource', back_populates='text_descriptors')
    descriptor = db.relationship('Descriptor', back_populates='text_resources')

    def __repr__(self):
        return '%s: %s' % (self.descriptor.name, self.text)


class Descriptor(db.Model):
    """
    Schema for descriptors that contain the name and values for an
    attribute of a resource.
    """
    __tablename__ = 'descriptors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    values = db.Column(db.PickleType)
    is_searchable = db.Column(db.Boolean)
    text_resources = db.relationship(
        'TextAssociation',
        back_populates='descriptor',
        cascade='save-update, merge, delete, delete-orphan'
    )
    option_resources = db.relationship(
        'OptionAssociation',
        back_populates='descriptor',
        cascade='save-update, merge, delete, delete-orphan'
    )

    def __repr__(self):
        return '<Descriptor \'%s\'>' % self.name

class RequiredOptionDescriptor(db.Model):
    __tablename__ = 'required_option_descriptor'
    id = db.Column(db.Integer, primary_key=True)
    descriptor_id = db.Column(db.Integer);
    @staticmethod
    def insert_required_option_descriptor():
        required_option_descriptor = RequiredOptionDescriptor(descriptor_id=-1)
        db.session.add(required_option_descriptor)
        db.session.commit()


class Resource(db.Model):
    """
    Schema for resources with relationships to descriptors.
    """
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    address = db.Column(db.String(250))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    text_descriptors = db.relationship(
        'TextAssociation',
        back_populates='resource',
        cascade='save-update, merge, delete, delete-orphan'
    )
    option_descriptors = db.relationship(
        'OptionAssociation',
        back_populates='resource',
        cascade='save-update, merge, delete, delete-orphan'
    )
    suggestions = db.relationship('Suggestion', backref='resource', uselist=True)

    def __repr__(self):
        return '<Resource \'%s\'>' % self.name

    @staticmethod
    def generate_fake(count=20, center_lat=39.951021, center_long=-75.197243):
        """Generate a number of fake resources for testing."""
        from sqlalchemy.exc import IntegrityError
        from random import randint
        from faker import Faker
        from geopy.geocoders import Nominatim

        geolocater = Nominatim()
        fake = Faker()

        num_options = 5
        options = []

        for i in range(num_options):
            options.append(Descriptor(
                name=fake.word(),
                values=['True', 'False'],
                is_searchable=fake.boolean()
            ))

        for i in range(count):

            # Generates random coordinates around Philadelphia.
            latitude = str(fake.geo_coordinate(
                center=center_lat,
                radius=0.01
            ))
            longitude = str(fake.geo_coordinate(
                center=center_long,
                radius=0.01
            ))

            location = geolocater.reverse(latitude + ', ' + longitude)

            # Create one or two resources with that location.
            for i in range(randint(1, 2)):
                resource = Resource(
                    name=fake.name(),
                    address=location.address,
                    latitude=latitude,
                    longitude=longitude
                )

                oa = OptionAssociation(option=randint(0, 1))
                oa.descriptor = options[randint(0, num_options - 1)]
                resource.option_descriptors.append(oa)

                ta = TextAssociation(text=fake.sentence(nb_words=10))
                ta.descriptor = Descriptor(
                    name=fake.word(),
                    values=[],
                    is_searchable=fake.boolean()
                )
                resource.text_descriptors.append(ta)

                db.session.add(resource)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()

    @staticmethod
    def get_resources_as_dicts(resources):
        # get required option descriptor
        req_opt_desc = RequiredOptionDescriptor.query.all()[0]
        req_opt_desc = Descriptor.query.filter_by(
            id=req_opt_desc.descriptor_id
        ).first()

        resources_as_dicts = []
        for resource in resources:
            res = resource.__dict__

            # set required option descriptor
            req = []
            if req_opt_desc is not None:
                associations = OptionAssociation.query.filter_by(
                    resource_id=resource.id,
                    descriptor_id=req_opt_desc.id
                ).all()
                req = [a.descriptor.values[a.option] for a in associations]
            res['requiredOpts'] = req

            # set ratings
            res['avg_rating'] = resource.get_avg_ratings()

            # .__dict__ returns the SQLAlchemy object as a dict, but it also adds a
            # field '_sa_instance_state' that we don't need, so we delete it.
            del res['_sa_instance_state']
            resources_as_dicts.append(res)
        return resources_as_dicts

    @staticmethod
    def print_resources():
        resources = Resource.query.all()
        for resource in resources:
            print resource
            print resource.address
            print '(%s , %s)' % (resource.latitude, resource.longitude)
            print resource.text_descriptors
            print resource.option_descriptors

    def get_avg_ratings(self):
        ratings = Rating.query.filter_by(resource_id=self.id).all()
        if not ratings:
            return 0.0
        total_sum = float(sum(r.rating for r in ratings))
        return '%.1f' % (total_sum / len(ratings))

    def get_all_ratings(self):
        ratings = Rating.query.filter_by(resource_id=self.id).all()
        ratings.sort(key=lambda r: r.submission_time, reverse=True)
        return ratings
