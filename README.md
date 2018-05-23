# Maps4All [![Circle CI](https://circleci.com/gh/hack4impact/maps4all.svg?style=svg)](https://circleci.com/gh/hack4impact/maps4all)  [![Code Climate](https://codeclimate.com/github/hack4impact/maps4all/badges/gpa.svg)](https://codeclimate.com/github/hack4impact/maps4all) [![Test Coverage](https://codeclimate.com/github/hack4impact/maps4all/badges/coverage.svg)](https://codeclimate.com/github/hack4impact/maps4all/coverage) [![Issue Count](https://codeclimate.com/github/hack4impact/maps4all/badges/issue_count.svg)](https://codeclimate.com/github/hack4impact/maps4all)

## Team Members

- Annie Meng
- Arman Tokanov
- Ben Sandler
- Brandon Obas
- Daniel Zhang
- Elizabeth Hamp
- Hana Pearlman
- Katie Jiang
- Kyle Rosenbluth
- Natasha Narang
- Rani Iyer
- Sanjay Subramanian
- Stephanie Shi
- Veronica Wharton

## Synopsis

A generalized Flask application for displaying location-based resources on a map.

## Setting up

If you have not yet done so, visit maps4all.org and create an account. This will guide you through the creation of your Heroku account and the installation of the Heroku tools. To develop locally on Windows 10, we (@sbue and myself, independently) used Windows Subsystem for Linux and additionally installed Heroku CLI in Ubuntu terminal and deployed with the client. 

##### Clone the repo

```
$ git clone https://github.com/hack4impact/maps4all.git
$ cd maps4all
```

##### Initialize a virtualenv
 
```
$ pip install virtualenv
$ virtualenv -p python3 venv
$ source venv/bin/activate
```
(If you're on a mac) Make sure xcode tools are installed
```
$ xcode-select --install
```

##### Install the dependencies

```
$ pip install -r requirements.txt
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

##### Set your environment variables

Create a `.env` file in your directory and include the following variables:
* `ADMIN_EMAIL` and `ADMIN_PASSWORD` allow you to login as an administrator to Maps4All on your local machine.
* `FILEPICKER_API_KEY` is an API key which you can obtain [here](https://dev.filestack.com/signup/free/).
* `MAIL_PASSWORD` and `MAIL_USERNAME` are your login credentials for [Sendgrid](https://sendgrid.com/).
* `GOOGLE_API_KEY`, `GOOGLE_API_1`, and `GOOGLE_API_2` are API keys for Google maps. They can be obtained [here](https://developers.google.com/maps/documentation/javascript/get-api-key#step-1-get-an-api-key-from-the-google-api-console).
* `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` allow you to use the Twilio API to send text messages. They can be obtained through the [Twilio console](https://www.twilio.com/login).

Your `.env` file should look something like this:
```
ADMIN_EMAIL=admin@maps4all.org
ADMIN_PASSWORD=password123
FILEPICKER_API_KEY=XXXXXXXXXXXXXXXX
MAIL_USERNAME=janedoe
MAIL_PASSWORD=password123
GOOGLE_API_KEY=XXXXXXXXXXXXXXXX
GOOGLE_API_1=XXXXXXXXXXXXXXXX
GOOGLE_API_2=XXXXXXXXXXXXXXXX
TWILIO_ACCOUNT_SID=XXXXXXXXXXXXXXXX
TWILIO_AUTH_TOKEN=XXXXXXXXXXXXXXXX
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
$ source venv/bin/activate
$ honcho start -f Local
```
Then navigate to `http://localhost:5000` on your preferred browser to open the web app.

## Project Structure


```
??? Procfile
??? README.md
??? app
?   ??? __init__.py
?   ??? account
?   ?   ??? __init__.py
?   ?   ??? forms.py
?   ?   ??? views.py
?   ??? admin
?   ?   ??? __init__.py
?   ?   ??? forms.py
?   ?   ??? views.py
?   ??? assets
?   ?   ??? scripts
?   ?   ?   ??? app.js
?   ?   ?   ??? vendor
?   ?   ?       ??? jquery.min.js
?   ?   ?       ??? semantic.min.js
?   ?   ?       ??? tablesort.min.js
?   ?   ??? styles
?   ?       ??? app.scss
?   ?       ??? vendor
?   ?           ??? semantic.min.css
?   ??? assets.py
?   ??? decorators.py
?   ??? email.py
?   ??? main
?   ?   ??? __init__.py
?   ?   ??? errors.py
?   ?   ??? forms.py
?   ?   ??? views.py
?   ??? models.py
?   ??? static
?   ?   ??? fonts
?   ?   ?   ??? vendor
?   ?   ??? images
?   ?   ??? styles
?   ?       ??? app.css
?   ??? templates
?   ?   ??? account
?   ?   ?   ??? email
?   ?   ?   ??? login.html
?   ?   ?   ??? manage.html
?   ?   ?   ??? register.html
?   ?   ?   ??? reset_password.html
?   ?   ?   ??? unconfirmed.html
?   ?   ??? admin
?   ?   ?   ??? index.html
?   ?   ?   ??? manage_user.html
?   ?   ?   ??? new_user.html
?   ?   ?   ??? registered_users.html
?   ?   ??? errors
?   ?   ??? layouts
?   ?   ?   ??? base.html
?   ?   ??? macros
?   ?   ?   ??? form_macros.html
?   ?   ?   ??? nav_macros.html
?   ?   ??? main
?   ?   ?   ??? index.html
?   ?   ??? partials
?   ?       ??? _flashes.html
?   ?       ??? _head.html
?   ??? utils.py
??? config.py
??? manage.py
??? requirements
?   ??? common.txt
?   ??? dev.txt
??? tests
    ??? test_basics.py
    ??? test_user_model.py
```

## License
[MIT License](LICENSE.md)
