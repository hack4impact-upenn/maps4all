from flask import current_app
from .. import db

class OptionAssociation(db.Model):
    """Association between a resource and a descriptor with an index
    for the value of the option
    """
    __tablename__ = 'option_associations'
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'),
                            primary_key=True)
    descriptor_id = db.Column(db.Integer, db.ForeignKey('descriptors.id'),
                              primary_key=True)
    option = db.Column(db.Integer)
    resource = db.relationship('Resource', 
                               back_populates='option_descriptors')
    descriptor = db.relationship('Descriptor', 
                                 back_populates='option_resources')

    def __repr__(self):
        return '%s: %s' % (self.descriptor.name,
                           self.descriptor.values[self.option])

class TextAssociation(db.Model):
    """Association between a resource and a descriptor with a text
    field for the value of the descriptor
    """
    __tablename__ = 'text_associations'
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'),
                            primary_key=True)
    descriptor_id = db.Column(db.Integer, db.ForeignKey('descriptors.id'),
                              primary_key=True)
    text = db.Column(db.String(64))
    resource = db.relationship('Resource', back_populates='text_descriptors')
    descriptor = db.relationship('Descriptor', back_populates='text_resources')

    def __repr__(self):
        return '%s: %s' % (self.descriptor.name, self.text)

class Descriptor(db.Model):
    """Schema for descriptors that contain the name and values for an 
    attribute of a resource
    """
    __tablename__ = 'descriptors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    values = db.Column(db.PickleType)
    text_resources = db.relationship('TextAssociation',
                                     back_populates='descriptor')
    option_resources = db.relationship('OptionAssociation',
                                       back_populates='descriptor')

    def __repr__(self):
        return '<Descriptor \'%s\'>' % self.name

class Resource(db.Model):
    """Schema for resources with relationships to descriptors """
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    address = db.Column(db.String(64))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    text_descriptors = db.relationship('TextAssociation',
                                       back_populates='resource')
    option_descriptors = db.relationship('OptionAssociation',
                                         back_populates='resource')

    def __repr__(self):
        return '<Resource \'%s\'>' % self.name

    @staticmethod
    def generate_fake(count=20, center_lat=39.951021, center_long=-75.197243):
        """Generate a number of fake resources for testing."""
        from sqlalchemy.exc import IntegrityError
        from random import seed, choice
        from faker import Faker
        from geopy.geocoders import Nominatim

        geolocater = Nominatim()
        fake = Faker()

        for i in range(count):

            # generates random coordinates around Philadelphia
            latitude=str(fake.geo_coordinate(
                center=center_lat,
                radius=0.01
            ))
            longitude=str(fake.geo_coordinate(
                center=center_long,
                radius=0.01
            ))

            location = geolocater.reverse(latitude + ', ' + longitude)
            resource = Resource(
                name=fake.name(),
                address=location.address, 
                latitude=latitude, 
                longitude=longitude
            )

            # alternates options between True and False
            oa = OptionAssociation(option= i % 2)
            oa.descriptor = Descriptor(name=fake.word(), 
                values=['True', 'False'])
            resource.option_descriptors.append(oa)

            ta = TextAssociation(text=fake.sentence(nb_words=10))
            ta.descriptor = Descriptor(name=fake.word(), values=[])
            resource.text_descriptors.append(ta)

            db.session.add(resource)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def print_resources():
        for resource in db.session.query(Resource).all():
            print resource 
            print resource.address
            print '(%s , %s)' % (resource.latitude, resource.longitude)
            print resource.text_descriptors
            print resource.option_descriptors





