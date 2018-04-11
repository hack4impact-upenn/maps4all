from .. import db
from .. models import Rating
import os


class OptionAssociation(db.Model):
    """
    Association between a resource and a descriptor with an index for the
    value of the option. Can have multiple OptionAssociation between an
    option descriptor and resource
    """
    __tablename__ = 'option_associations'
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey(
        'resources.id', ondelete='CASCADE'))
    descriptor_id = db.Column(db.Integer, db.ForeignKey(
        'descriptors.id', ondelete='CASCADE'))
    option = db.Column(db.Integer)
    resource = db.relationship('Resource', back_populates='option_descriptors')
    descriptor = db.relationship(
        'Descriptor', back_populates='option_resources')

    def generate_fake():
        options = []
        options.append(Descriptor(
            name='Residential Program',
            values=['Arts House', 'Cultures Collective', 'Mentors Program'],
            dtype='option',
            is_searchable=False
        ))
        options.append(Descriptor(
            name='Room Options',
            values=['Singles', 'Doubles', 'Triples'],
            dtype='option',
            is_searchable=True
        ))
        options.append(Descriptor(
            name='Dorm Type',
            values=['Freshmen', 'Upperclassmen', 'Four-year'],
            dtype='option',
            is_searchable=True
        ))
        return options

    def generate_fake():
        options = []
        options.append(Descriptor(
            name='Residential Program',
            values=['Arts House', 'Cultures Collective', 'Mentors Program'],
            is_searchable=False
        ))
        options.append(Descriptor(
            name='Room Options',
            values=['Singles', 'Doubles', 'Triples'],
            is_searchable=True
        ))
        options.append(Descriptor(
            name='Dorm Type',
            values=['Freshmen', 'Upperclassmen', 'Four-year'],
            is_searchable=True
        ))
        return options

    def __repr__(self):
        return "{}: {}".format(self.descriptor.name,
                               self.descriptor.values[self.option])


class TextAssociation(db.Model):
    """
    Association between a resource and a descriptor with a text field for the
    value of the descriptor. Currently only support one text association between
    a resource and descriptor.
    """
    __tablename__ = 'text_associations'
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey(
        'resources.id', ondelete='CASCADE'))
    descriptor_id = db.Column(db.Integer, db.ForeignKey(
        'descriptors.id', ondelete='CASCADE'))
    text = db.Column(db.Text)
    resource = db.relationship('Resource', back_populates='text_descriptors')
    descriptor = db.relationship('Descriptor', back_populates='text_resources')

    def __repr__(self):
        return "{}: {}".format(self.descriptor.name, self.text)


class HyperlinkAssociation(db.Model):
    """
    Association between a resource and a descriptor with a hyperlink url for the
    value of the descriptor.
    """
    __tablename__ = 'hyperlink_associations'
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey(
        'resources.id', ondelete='CASCADE'))
    descriptor_id = db.Column(db.Integer, db.ForeignKey(
        'descriptors.id', ondelete='CASCADE'))
    url = db.Column(db.String(250))
    resource = db.relationship(
        'Resource', back_populates='hyperlink_descriptors')
    descriptor = db.relationship(
        'Descriptor', back_populates='hyperlink_resources')

    def __repr__(self):
        return "{}: {}".format(self.descriptor.name, self.url)


class Descriptor(db.Model):
    """
    Schema for descriptors that contain the name and values for an
    attribute of a resource.
    """
    __tablename__ = 'descriptors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    # should only have value for option descriptor
    values = db.Column(db.PickleType, default=[])
    is_searchable = db.Column(db.Boolean)
    # descriptor type, can be 'Text', 'Optional', or 'Hyperlink'
    dtype = db.Column(db.String(15))
    text_resources = db.relationship(
        'TextAssociation',
        back_populates='descriptor',
        cascade='all, delete-orphan'
    )
    option_resources = db.relationship(
        'OptionAssociation',
        back_populates='descriptor',
        cascade='all, delete-orphan'
    )
    hyperlink_resources = db.relationship(
        'HyperlinkAssociation',
        back_populates='descriptor',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return "<Descriptor '{}'>".format(self.name)

    def value_string(self):
        if not self.values:
            return ''
        l = list(self.values)
        l.sort()
        return ', '.join(map(str, l))


class RequiredOptionDescriptor(db.Model):
    """ Option descriptor designated as a required option descriptor meaning
    that all resources need to have an option association for this descriptor.
    Restricted to one.
    """
    __tablename__ = 'required_option_descriptor'
    id = db.Column(db.Integer, primary_key=True)
    descriptor_id = db.Column(db.Integer)  # -1 if none

    @staticmethod
    def init_required_option_descriptor():
        required_option_descriptor = RequiredOptionDescriptor(descriptor_id=-1)
        db.session.add(required_option_descriptor)
        db.session.commit()


class Resource(db.Model):
    """
    Schema for resources with relationships to descriptors.
    """
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    address = db.Column(db.String(500))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    text_descriptors = db.relationship(
        'TextAssociation',
        back_populates='resource',
        cascade='all, delete-orphan'
    )
    option_descriptors = db.relationship(
        'OptionAssociation',
        back_populates='resource',
        cascade='all, delete-orphan'
    )
    hyperlink_descriptors = db.relationship(
        'HyperlinkAssociation',
        back_populates='resource',
        cascade='all, delete-orphan'
    )
    suggestions = db.relationship(
        'Suggestion',
        backref='resource',
        uselist=True,
        cascade='all, delete-orphan'
    )
    ratings = db.relationship(
        'Rating',
        backref='resource',
        uselist=True,
        cascade='all, delete-orphan',
    )

    def __repr__(self):
        return "<Resource '{}'>".format(self.name)

    @staticmethod
    def generate_fake(count=20, center_lat=39.951021, center_long=-75.197243):
        """Generate a number of fake resources for testing."""
        from sqlalchemy.exc import IntegrityError
        from random import randint
        from faker import Faker
        import googlemaps
        fake = Faker()

        num_options = 3
        options = OptionAssociation.generate_fake()
        text_serve = Descriptor(
            name='Who We Serve',
            dtype='text',
            is_searchable=True
        )
        text_about = Descriptor(
            name='About',
            dtype='text',
            is_searchable=True
        )

        hyperlink_website = Descriptor(
            name='Website',
            dtype='hyperlink',
            is_searchable=False
        )

        gmaps = googlemaps.Client(key=os.environ['GOOGLE_API_KEY'])

        # Generate resources
        for i in range(count):
            # Generates random coordinates around Philadelphia.
            latitude = fake.geo_coordinate(
                center=center_lat,
                radius=0.01
            )
            longitude = fake.geo_coordinate(
                center=center_long,
                radius=0.01
            )
            # Create an address with reverse geocoding
            location = gmaps.reverse_geocode((latitude, longitude))[0]

            # Create one or two resources with that location.
            for i in range(randint(1, 2)):
                resource = Resource(
                    name=fake.name(),
                    address=location['formatted_address'],
                    latitude=latitude,
                    longitude=longitude
                )
                # Add option descriptors
                oa = OptionAssociation(option=randint(0, num_options - 1))
                oa.descriptor = options[randint(0, 2)]
                resource.option_descriptors.append(oa)
                # Add text descriptors
                for tdescriptor in [text_serve, text_about]:
                    ta = TextAssociation(text=fake.sentence(
                        nb_words=10), descriptor=tdescriptor)
                    resource.text_descriptors.append(ta)
                ha = HyperlinkAssociation(
                    url='http://maps4all.org', descriptor=hyperlink_website)
                resource.hyperlink_descriptors.append(ha)

                db.session.add(resource)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()

    @staticmethod
    def get_resources_as_dicts(resources):
        # get required option descriptor
        req_opt_desc = RequiredOptionDescriptor.query.all()
        if req_opt_desc:
            req_opt_desc = req_opt_desc[0]
            req_opt_desc = Descriptor.query.filter_by(
                id=req_opt_desc.descriptor_id
            ).first()

        resources_as_dicts = []
        for resource in resources:
            res = resource.__dict__

            # set required option descriptor
            req = []
            if req_opt_desc:
                associations = OptionAssociation.query.filter_by(
                    resource_id=resource.id,
                    descriptor_id=req_opt_desc.id
                ).all()
                req = [a.descriptor.values[a.option] for a in associations]
            res['requiredOpts'] = req

            # set ratings
            res['avg_rating'] = resource.get_avg_ratings()

            if '_sa_instance_state' in res:
                del res['_sa_instance_state']
            resources_as_dicts.append(res)
        return resources_as_dicts


    @staticmethod
    def get_associations(resource):
        associations = {}
        if resource is None:
            return json.dumps(associations)
        for td in resource.text_descriptors:
            associations[td.descriptor.name] = td.text
        for od in resource.option_descriptors:
            val = od.descriptor.values[od.option]
            values = set()
            # multiple option association values
            if associations.get(od.descriptor.name):
                curr = associations.get(od.descriptor.name)
                curr.append(val)
                values = set(curr)
            else:
                values.add(val)
            associations[od.descriptor.name] = list(values)
        return associations

    @staticmethod
    def print_resources():
        resources = Resource.query.all()
        for resource in resources:
            print(resource)
            print(resource.address)
            print("({}, {})".format(resource.latitude, resource.longitude))
            print(resource.text_descriptors)
            print(resource.option_descriptors)

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
