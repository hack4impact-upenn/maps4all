from .. import db

from sqlalchemy import desc

class CsvStorage(db.Model):
    __tablename__ = 'csv_storages'
    id = db.Column(db.Integer, primary_key=True)
    date_uploaded = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String, default='reset') # or 'update'
    csv_rows = db.relationship('CsvRow', backref='csv_storage',
                               uselist=True, cascade='delete')
    csv_descriptors = db.relationship('CsvDescriptor', backref='csv_storage',
                                      uselist=True, cascade='delete')
    csv_descriptors_remove = db.relationship('CsvDescriptorRemove', backref='csv_storage',
                                             uselist=True, cascade='delete')

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
                            values.add(v)
                        desc.values = values
                        db.session.add(desc)
        db.session.commit()

    @staticmethod
    def most_recent(user):
        return CsvStorage.query.filter_by(user=user).order_by(
            desc(CsvStorage.date_uploaded)
        ).limit(1).first()

class CsvRow(db.Model):
    __tablename__= 'csv_rows'
    id = db.Column(db.Integer, primary_key=True)
    csv_storage_id = db.Column(db.Integer, db.ForeignKey('csv_storages.id'))
    data = db.Column(db.PickleType) # json
    resource_id = db.Column(db.Integer) # no foreign key because could be null

class CsvDescriptor(db.Model):
    __tablename__= 'csv_descriptors'
    id = db.Column(db.Integer, primary_key=True)
    csv_storage_id = db.Column(db.Integer, db.ForeignKey('csv_storages.id'))
    name = db.Column(db.String(64))
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
    __tablename__= 'csv_descriptors_remove'
    id = db.Column(db.Integer, primary_key=True)
    csv_storage_id = db.Column(db.Integer, db.ForeignKey('csv_storages.id'))
    descriptor_id = db.Column(db.Integer, db.ForeignKey('descriptors.id'))
    name = db.Column(db.String(64))
