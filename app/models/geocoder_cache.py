from .. import db


class GeocoderCache(db.Model):
    """ Cache results from address geocoding to avoid going over limit """
    __tablename__ = 'geocoder_cache'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(500), index=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)