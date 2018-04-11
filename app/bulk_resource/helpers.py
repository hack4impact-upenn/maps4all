import os
import geocoder

from flask import jsonify

from .. import db
from ..models import (
    GeocoderCache
)

def validate_address(data, address):
    """
    Returns gstatus to check validity of address using Google Maps API.
    If the address is valid, gstatus will be 'OK'. Otherwise, the gstatus will
    be a helpful error message.
    """
    # See if address exists in cache
    cached = GeocoderCache.query.filter_by(
        address=address
    ).first()
    if cached is None:
        # Toggle API to avoid Google geocoder API limit - temp solution
        if data['count'] % 45 == 0:
            if os.environ.get('GOOGLE_API_KEY') == os.environ.get('GOOGLE_API_1'):
                os.environ['GOOGLE_API_KEY'] = os.environ.get('GOOGLE_API_2')
            else:
                os.environ['GOOGLE_API_KEY'] = os.environ.get('GOOGLE_API_1')
        g = geocoder.google(address, key=os.environ.get('GOOGLE_API_KEY'))
        if g.status != 'OK':
            return g.status
        else:
            geo = GeocoderCache(
                address=address,
                latitude=g.latlng[0],
                longitude=g.latlng[1]
            )
            db.session.add(geo)
    return 'OK'
