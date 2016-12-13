from flask.ext.assets import Bundle

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

# Define order or issues on heroku
vendor_js = Bundle(
    'vendor/jquery.min.js',
    'vendor/semantic.min.js',
    'vendor/tablesort.min.js',
    'vendor/*.js',
    filters='jsmin',
    output='scripts/vendor.js'
)
