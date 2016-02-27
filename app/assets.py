from flask.ext.assets import Bundle

app_css = Bundle(
    'app.scss',
    filters='scss',
    output='styles/app.css'
)

app_js = Bundle(
    'app.js',
    filters='jsmin',
    output='scripts/app.js'
)

vendor_css = Bundle(
    'vendor/semantic.min.css',
    output='styles/vendor.css'
)

vendor_js = Bundle(
    'vendor/jquery.min.js',
    'vendor/semantic.min.js',
    'vendor/tablesort.min.js',
    filters='jsmin',
    output='scripts/vendor.js'
)

gmaps_js = Bundle(
    'gmaps.js',
    filters='jsmin',
    output='scripts/gmaps.js'
)

googlemaps_js = Bundle(
    'googlemaps.js',
    filters='jsmin',
    output='scripts/googlemaps.js'
)