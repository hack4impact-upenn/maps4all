from .. import db


''' Cache results from address geocoding to avoid going over limit '''
class GeocoderCache(db.Model):
    __tablename__ = 'geocoder_cache'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(250), index=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)