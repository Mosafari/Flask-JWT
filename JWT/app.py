# import flask
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# creates Flask object
app = Flask(__name__)
# configuration
app.config['SECRET_KEY'] = 'your secret key'
# database name
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# creates SQLALCHEMY object
db = SQLAlchemy(app)

# Database ORMs
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(70), unique = True)
    password = db.Column(db.String(80))
    date = db.Column(db.TEXT, default='')
    day = db.Column(db.String(20), default = '')
    
