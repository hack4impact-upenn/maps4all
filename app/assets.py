from flask_assets import Bundle

app_css = Bundle(
    '*.scss',
    filters='scss',
    output='styles/app.css'
)

app_js = Bundle(
    '*.js',
    filters='jsmin',
    output='scripts/app.js'
)

vendor_css = Bundle(
    'vendor/*.css',
    output='styles/vendor.css'
)

# Need to specify vendor order or JS errors on heroku
vendor_js = Bundle(
    'vendor/jquery.min.js',
    'vendor/semantic.min.js',
    'vendor/tablesort.min.js',
    'vendor/address-autocomplete.js',
    'vendor/async.js',
    'vendor/handlebars-v4.0.5.js',
    'vendor/oms.min.js',
    'vendor/papaparse.min.js',
    'vendor/zxcvbn.js',
    filters='jsmin',
    output='scripts/vendor.js'
)
