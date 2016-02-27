from .. import db, login_manager

class Association(db.Model):
    __tablename__ = 'associations'
    pin_id = db.Column(db.Integer, db.ForeignKey('pins.id'), primary_key=True)
    descriptor_id = db.Column(db.Integer, db.ForeignKey('descriptors.id'), primary_key=True)
    value = db.Column(db.String(64))
    pins = relationship("Pin", back_populates="descriptors")
    descriptors = relationship("Descriptor", back_populates="pins")

class Descriptor(db.Model):
    __tablename__ = 'descriptors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    category = db.Column(db.String(64), index=True)
    pins = relationship("Association", back_populates="descriptors")

class Pin(db.Model):
    __tablename__ = 'pins'
    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float)
    long = db.Column(db.Float)
    descriptors = relationship("Association", back_populates="pins")
