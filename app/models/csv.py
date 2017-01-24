from .. import db

from sqlalchemy import desc


class CsvStorage(db.Model):
    """ General CSV Storage container encompassing one CSV """
    __tablename__ = 'csv_storages'
    id = db.Column(db.Integer, primary_key=True)
    date_uploaded = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String, default='reset') # or 'update'
    csv_rows = db.relationship('CsvRow', backref='csv_storage',
                               uselist=True, cascade='delete, delete-orphan')
    csv_descriptors = db.relationship('CsvDescriptor', backref='csv_storage',
                                      uselist=True, cascade='delete, delete-orphan')
    csv_descriptors_remove = db.relationship('CsvDescriptorRemove', backref='csv_storage',
                                             uselist=True, cascade='delete, delete-orphan')

    """ Find option values of option descriptors in the CSV """
    def set_desc_values(self):
        all_descs = self.csv_descriptors
        opt_descs = dict([(d.name, d) for d in all_descs if d.descriptor_type == 'option'])
        for row in self.csv_rows:
            for key in row.data:
                if key and key != 'Name' and key != 'Address' and key in opt_descs:
                    val = row.data[key]
                    if val:
                        desc = opt_descs[key]
                        values = set()
                        if desc.values:
                            values = desc.values
                        val = val.split(';')
                        for v in val:
                            if v.strip():
                                values.add(v.strip())
                        desc.values = values
                        db.session.add(desc)
        db.session.commit()

    @staticmethod
    def most_recent(user):
        return CsvStorage.query.filter_by(user=user).order_by(
            desc(CsvStorage.date_uploaded)
        ).limit(1).first()


class CsvRow(db.Model):
    """ Representation of a row in a CSV
    - data field is a dictionary of header name to row value
    - can be linked to an existing resource in the app for updates
    """
    __tablename__= 'csv_rows'
    id = db.Column(db.Integer, primary_key=True)
    csv_storage_id = db.Column(db.Integer, db.ForeignKey('csv_storages.id', ondelete='CASCADE'))
    data = db.Column(db.PickleType) # json
    resource_id = db.Column(db.Integer) # no foreign key because could be null


class CsvDescriptor(db.Model):
    """ Representation of a descriptor (header) in a CSV
    - can be linked to an existing descriptor in the app for updates
    - values field will only contain values found from the CSV so if it links to
    an existing descriptor in the app, the existing values won't show up here unless
    also present in the CSV
    """
    __tablename__= 'csv_descriptors'
    id = db.Column(db.Integer, primary_key=True)
    csv_storage_id = db.Column(db.Integer, db.ForeignKey('csv_storages.id', ondelete='CASCADE'))
    name = db.Column(db.String(500))
    descriptor_type = db.Column(db.String, default='text') # or 'option'
    values = db.Column(db.PickleType) # list of string options from CSV ONLY
    descriptor_id = db.Column(db.Integer) # no foreign key because could be null

    def value_string(self):
        if not self.values:
            return ''
        l = list(self.values)
        l.sort()
        return ', '.join(map(str, l))


class CsvDescriptorRemove(db.Model):
    """
    (CURRENTLY NOT IN USE)
    Representation of a descriptor (header) not in the CSV but in the app
    - In updates, if a descriptor is in the app but not in the new CSV then we
    assume deletion of this descriptor
    """
    __tablename__= 'csv_descriptors_remove'
    id = db.Column(db.Integer, primary_key=True)
    csv_storage_id = db.Column(db.Integer, db.ForeignKey('csv_storages.id', ondelete='CASCADE'))
    descriptor_id = db.Column(db.Integer, db.ForeignKey('descriptors.id', ondelete='CASCADE'))
    name = db.Column(db.String(500))


class RequiredOptionDescriptorConstructor(db.Model):
    __tablename__ = 'required_option_descriptor_constructor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    values = db.Column(db.PickleType)
    missing_dict = db.Column(db.PickleType)
