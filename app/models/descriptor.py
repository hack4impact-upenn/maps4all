class Option(db.Model):
    __tablename__ = 'options'
    pin_id = db.Column(db.Integer, db.ForeignKey('pins.id'), primary_key=True)
    descriptor_id = db.Column(db.Integer, db.ForeignKey('descriptors.id'), primary_key=True)
    value = db.Column(db.String(64))
    #pins = relationship("Pin", back_populates="descriptors")
    #descriptors = relationship("Descriptor", back_populates="pins")

class Text(db.Model):
    __tablename__ = 'text'
    pin_id = db.Column(db.Integer, db.ForeignKey('pins.id'), primary_key=True)
    descriptor_id = db.Column(db.Integer, db.ForeignKey('descriptors.id'), primary_key=True)
    value = db.Column(db.String(64))

class Descriptor(db.Model):
    __tablename__ = 'descriptors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    category = db.Column(db.String(64), index=True)

class Pin(db.Model):
    __tablename__ = 'pins'
    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float)
    long = db.Column(db.Float)
