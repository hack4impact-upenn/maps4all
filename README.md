# Maps4All [![Circle CI](https://circleci.com/gh/hack4impact/maps4all.svg?style=svg)](https://circleci.com/gh/hack4impact/maps4all)  [![Code Climate](https://codeclimate.com/github/hack4impact/maps4all/badges/gpa.svg)](https://codeclimate.com/github/hack4impact/maps4all) [![Test Coverage](https://codeclimate.com/github/hack4impact/maps4all/badges/coverage.svg)](https://codeclimate.com/github/hack4impact/maps4all/coverage) [![Issue Count](https://codeclimate.com/github/hack4impact/maps4all/badges/issue_count.svg)](https://codeclimate.com/github/hack4impact/maps4all)

## Team Members

- Elizabeth Hamp
- Natasha Narang
- Arman Tokanov
- Veronica Wharton
- Daniel Zhang
- Annie Meng
- Stephanie Shi
- Sanjay Subramanian
- Ben Sandler
- Brandon Obas
- Kyle Rosenbluth
- Rani Iyer

## Synopsis

A Flask application template with the boilerplate code already done for you.

## What's included?

* Blueprints
* User and permissions management
* Flask-SQLAlchemy for databases
* Flask-WTF for forms
* Flask-Assets for asset management and SCSS compilation
* Flask-Mail for sending emails
* Automatic SSL + gzip compression

## Setting up

##### Clone the repo

```
$ git clone https://github.com/hack4impact/maps4all.git
$ cd maps4all
```

##### Initialize a virtualenv

```
$ pip install virtualenv
$ virtualenv env
$ source env/bin/activate
```
(If you're on a mac) Make sure xcode tools are installed
```
$ xcode-select --install
```

##### Install the dependencies

```
$ pip install -r requirements/common.txt
$ pip install -r requirements/dev.txt
```

##### Other dependencies for running locally

You need to install [Foreman](https://ddollar.github.io/foreman/) and [Redis](http://redis.io/). Chances are, these commands will work:

```
$ gem install foreman
```

For Mac (using [homebrew](http://brew.sh/)):

```
$ brew install redis
```

For Linux (Fedora)

```
$ sudo dnf install redis
```

For Linux (Debian/Ubuntu):

```
$ sudo apt-get install redis-server
```

If you don't want to install redis locally, you can use Redis container with docker

```
$ docker pull redis:latest
$ docker run -d -p 6379:6379 --name maps4all-redis redis:latest
```


##### Create the database

```
$ python manage.py recreate_db
```

##### Other setup (e.g. creating roles in database)

```
$ python manage.py setup_dev
```

##### [Optional] Add fake data to the database

```
$ python manage.py add_fake_data
```

## Running the app

```
$ source env/bin/activate
$ foreman start -f Local
```

**Note**: if you are using Redis container with docker, you can ignore the error that `foreman` will display when you run the `foreman` command above. `foreman` will try to start the redis-server locally and it will not find the `redis-server` command. This is fine as long as you followed the [instructions above](#other-dependencies-for-running-locally) to run Redis in a container. The error should look like this

```
$ foreman start -f Local
10:22:56 redis.1  | unknown command: redis-server
10:22:56 web.1    | started with pid 14409
10:22:56 worker.1 | started with pid 14410
10:22:57 worker.1 | 10:22:57 RQ worker u'rq:worker:dev.14410' started, version 0.5.6
10:22:57 worker.1 | 10:22:57 
10:22:57 worker.1 | 10:22:57 *** Listening on default...
10:22:57 web.1    |  * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
10:22:57 web.1    |  * Restarting with stat
```

## Project Structure


```
├── Procfile
├── README.md
├── app
│   ├── __init__.py
│   ├── account
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── views.py
│   ├── admin
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── views.py
│   ├── assets
│   │   ├── scripts
│   │   │   ├── app.js
│   │   │   └── vendor
│   │   │       ├── jquery.min.js
│   │   │       ├── semantic.min.js
│   │   │       └── tablesort.min.js
│   │   └── styles
│   │       ├── app.scss
│   │       └── vendor
│   │           └── semantic.min.css
│   ├── assets.py
│   ├── decorators.py
│   ├── email.py
│   ├── main
│   │   ├── __init__.py
│   │   ├── errors.py
│   │   ├── forms.py
│   │   └── views.py
│   ├── models.py
│   ├── static
│   │   ├── fonts
│   │   │   └── vendor
│   │   ├── images
│   │   └── styles
│   │       └── app.css
│   ├── templates
│   │   ├── account
│   │   │   ├── email
│   │   │   ├── login.html
│   │   │   ├── manage.html
│   │   │   ├── register.html
│   │   │   ├── reset_password.html
│   │   │   └── unconfirmed.html
│   │   ├── admin
│   │   │   ├── index.html
│   │   │   ├── manage_user.html
│   │   │   ├── new_user.html
│   │   │   └── registered_users.html
│   │   ├── errors
│   │   ├── layouts
│   │   │   └── base.html
│   │   ├── macros
│   │   │   ├── form_macros.html
│   │   │   └── nav_macros.html
│   │   ├── main
│   │   │   └── index.html
│   │   └── partials
│   │       ├── _flashes.html
│   │       └── _head.html
│   └── utils.py
├── config.py
├── manage.py
├── requirements
│   ├── common.txt
│   └── dev.txt
└── tests
    ├── test_basics.py
    └── test_user_model.py
```

## License
[MIT License](LICENSE.md)
