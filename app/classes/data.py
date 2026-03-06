
# This file defines the database models for users and stories.
# Models are like blueprints for the data stored in the app.

from datetime import datetime, timezone  # For dates and times
from flask_login import UserMixin, current_user  # For login features
from google.oauth2 import id_token  # For Google login
from google.auth.transport import requests  # For Google login
from app import db  # Database
import os

# User model: stores info about each user
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each user
    google_id = db.Column(db.String(100), unique=True, nullable=False)  # Google ID
    email_ousd = db.Column(db.String(120), unique=True, nullable=False)  # School email
    email_personal = db.Column(db.String(120), unique=True)  # Personal email
    fname = db.Column(db.String(100), nullable=False)  # First name
    lname = db.Column(db.String(100), nullable=False)  # Last name
    image = db.Column(db.LargeBinary)  # Profile image as binary data
    google_image = db.Column(db.String(100)) # link to google profile image
    mobile = db.Column(db.String(15))  # Mobile number
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # When user was created
    last_login = db.Column(db.DateTime)  # Last login time
    aeriesid = db.Column(db.Integer)  # School ID
    gid = db.Column(db.String(50))  # Google ID
    role = db.Column(db.String(20))  # ie staff, student

    # Link to stories written by the user
    stories = db.relationship('Story', back_populates='author')

    def __repr__(self):
        return f"{self.fname} {self.lname} Role: {self.role}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'google_id': self.google_id,
            'email_ousd': self.email_ousd,
            'email_personal': self.email_personal,
            'fname': self.fname,
            'lname': self.lname,
            'image': self.image,
            'created_at': self.created_at,
            'last_login': self.last_login
        }
    
    # Check if the user's Google login is valid
    def is_valid(self):
        try:
            # Check the Google ID token
            idinfo = id_token.verify_oauth2_token(current_user.google_id_token, requests.Request(), os.environ['future_google_client_id'])
        except:
            # Invalid token
            return False
        else:
            # Token is valid
            return True

# Story model: stores info about each story
class Story(db.Model):
    __tablename__ = 'story'
    
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each story
    content = db.Column(db.String(1000))  # Story content
    title = db.Column(db.String(100))  # Story title
    createdate = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # When story was created
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # user unique ID
    author = db.relationship('User', back_populates='stories')  # Link to user
    image = db.Column(db.LargeBinary)
    audio = db.Column(db.LargeBinary)


