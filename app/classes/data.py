
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

# Project model: stores info about each project
class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each project
    name = db.Column(db.String(100), nullable=False)  # Project title
    course = db.Column(db.String(100), nullable=False)
    product = db.Column(db.String(1000))  # Project description
    learning_materials = db.Column(db.String(1000))  # Project description
    description = db.Column(db.String(1000))  # Project description
    createDateTime = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # Creation date
    updated_at = db.Column(db.DateTime)  # Last update date
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Owner user ID
    owner = db.relationship('User', backref='projects')  # Link to user
    status = db.Column(db.String(50))  # Project status
    milestone = db.Column(db.String(200))  # Current milestone
    # Add more fields as needed to match MongoEngine model
    milestones = db.relationship('Milestone', back_populates='project')


    def __repr__(self):
        return f"<Project {self.title} (Owner ID: {self.owner_id})>"

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.createDateTime,
            'updated_at': self.updated_at,
            'owner_id': self.owner_id,
            'status': self.status,
            'milestone': self.milestone
        }

# Milestone model: stores info about each project milestone
class Milestone(db.Model):
    __tablename__ = 'milestones'

    oid = db.Column(db.Integer, primary_key=True)  # Unique ID for each milestone
    name = db.Column(db.String(100), nullable=False)  # Milestone title
    description = db.Column(db.String(500))  # Milestone description
    due_date = db.Column(db.DateTime)  # Due date for milestone
    status = db.Column(db.String(50))  # Milestone status
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))  # Associated project
    project = db.relationship('Project', back_populates='milestones')  # Link to user
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Associated user
    posts = db.relationship('ProjPost', back_populates='milestone')


    def __repr__(self):
        return f"<Milestone {self.name} (Project ID: {self.project_id})>"

    def to_dict(self):
        return {
            'id': self.oid,
            'name': self.name,
            'description': self.description,
            'due_date': self.due_date,
            'status': self.status,
            'project_id': self.project_id
        }

# ProjPost model: stores info about each project post
class ProjPost(db.Model):
    __tablename__ = 'projposts'

    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each post
    post_type = db.Column(db.String(100)) 
    confidence = db.Column(db.Integer)
    satisfaction = db.Column(db.Integer)
    content = db.Column(db.String(2000))  # Post content
    intention = db.Column(db.String(2000))  # Post content
    reflection = db.Column(db.String(2000))  # Post content
    discussion = db.Column(db.String(2000))  # Post content
    createDateTime = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # Creation date
    updated_at = db.Column(db.DateTime)  # Last update date
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Author user ID
    author = db.relationship('User', backref='projposts')  # Link to user
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))  # Associated project
    milestone_id = db.Column(db.Integer, db.ForeignKey('milestones.oid'))
    milestone = db.relationship('Milestone', back_populates='posts')


    def __repr__(self):
        return f"<ProjPost (Project ID: {self.project_id}, Author ID: {self.author_id})>"

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'author_id': self.author_id,
            'project_id': self.project_id
        }


