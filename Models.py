from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///JobMaster'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
db = SQLAlchemy(app)


class Persons(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    linkedinURL = db.Column(db.String(200), unique=False, nullable=True)
    firstname = db.Column(db.String(80), unique=False, nullable=True)
    lastname = db.Column(db.String(80), unique=False, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    company = db.Column(db.String(80), unique=False, nullable=True)
    domain = db.Column(db.String(80), unique=False, nullable=True)
    job = db.Column(db.String(200), unique=False, nullable=True)
    contacted = db.Column(db.Boolean, unique=False, nullable=False, default=False)

    def __repr__(self):
        return '<Person '+str(self.firstname)+' from Company '+str(self.company)+' with email '+str(self.email)+'>'

class LinkedInURLs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    linkedinURL = db.Column(db.String(200), unique=True, nullable=False)
    scraped = db.Column(db.Boolean, unique=False, nullable=False, default=False)

    def __repr__(self):
        return '<Linkedin URL '+str(self.linkedinURL)+' Visited: '+str(self.scraped)+'>'

db.create_all()
