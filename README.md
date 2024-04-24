

# Setup
## python environment and packages
### setup virtual env
`python -m venv .venv`

### activate the virtual env
`source .venv/bin/activate`

### install python packages
`pip install -r requirements.txt`

## setup .env file
`cp .sample-env .env`

### setup env variables
In the .env files you need to setup connection details to 
Postgres:
CREATE DATABASE genaiappbuilder;
CREATE ROLE genaiappbuilder WITH LOGIN PASSWORD 'strong_password'; 
ALTER DATABASE genaiappbuilder OWNER TO genaiappbuilder;

Redis:
redis-cli
ACL SETUSER user >password on allchannels allkeys +get +set +del allcommands
ACL SETUSER genaiappbuilder >Jg5X9gnGtzC5AMy on allchannels allkeys +get +set +del allcommands
You also need to set a secret django key:

`
import string
import random

''.join(random.SystemRandom().choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(50))
`

## install node dependencies
`npm install`

## install css
### Compile Tailwind CSS code
`npx tailwindcss -i ./static/src/input.css -o ./static/src/output.css --watch`

### Copy flowbite js to static
`cp **/flowbite.min.js static/src`


# Run
## Run migrations
`python manage.py migrate`

## Run server locally
`python manage.py runserver`