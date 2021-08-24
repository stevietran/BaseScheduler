import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

basedir = os.path.abspath(os.path.dirname(__file__))

# Create the connexion application instance
app = Flask(__name__)

# Configure the SqlAlchemy part of the app instance
app.config["SQLALCHEMY_ECHO"] = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'dbTest.db')
app.config['SECRET_KEY'] = "random string"
app.config["DEBUG"] = True

# Create the SqlAlchemy db instance
session_options = {'autocommit': False, 'autoflush': False}
db = SQLAlchemy(app, session_options=session_options)
