from flask import current_app
from .. import db

class OptionAssociation(db.Model):
    __tablename__ = 'optionassociations'
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), primary_key=True)
    descriptor_id = db.Column(db.Integer, db.ForeignKey('descriptors.id'), primary_key=True)
    option = db.Column(db.Integer)
    resource = db.relationship('Resource', back_populates='option_descriptors')
    descriptor = db.relationship('Descriptor', back_populates='option_resources')

class TextAssociation(db.Model):
    __tablename__ = 'textassociations'
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), primary_key=True)
    descriptor_id = db.Column(db.Integer, db.ForeignKey('descriptors.id'), primary_key=True)
    text = db.Column(db.String(64))
    resource = db.relationship('Resource', back_populates='text_descriptors')
    descriptor = db.relationship('Descriptor', back_populates='text_resources')

class Descriptor(db.Model):
    __tablename__ = 'descriptors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    #category = db.Column(db.String(64), index=True)
    values = db.Column(db.PickleType)
    text_resources = db.relationship('TextAssociation', back_populates='descriptor')
    option_resources = db.relationship('OptionAssociation', back_populates='descriptor')

    def __repr__(self):
        return '<Descriptor \'%s\'>' % self.name

class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    lat = db.Column(db.Float)
    long = db.Column(db.Float)
    text_descriptors = db.relationship('TextAssociation', back_populates='resource')
    option_descriptors = db.relationship('OptionAssociation', back_populates='resource')

    def __repr__(self):
        return '<Resource \'%s\'>' % self.name


