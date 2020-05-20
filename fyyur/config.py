import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:Password@localhost:5432/fyyur'

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgres://postgres:Password@localhost:5432/fyyur'
