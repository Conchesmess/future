
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

    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    team = db.relationship('Team', back_populates='members')
    stories = db.relationship('Story', back_populates='author')
    projects = db.relationship('Project', back_populates='owner')



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
    content = db.Column(db.Text())  # Story content
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
    learning_materials = db.Column(db.Text())  # Project description
    description = db.Column(db.Text())  # Project description
    createDateTime = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # Creation date
    updated_at = db.Column(db.DateTime)  # Last update date
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Owner user ID
    owner = db.relationship('User', back_populates='projects')  # Link to user
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
    description = db.Column(db.String(1000))  # Milestone description
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
    content = db.Column(db.Text()) 
    intention = db.Column(db.Text())  
    reflection = db.Column(db.Text())  
    discussion = db.Column(db.Text())  
    createDateTime = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # Creation date
    updated_at = db.Column(db.DateTime)  # Last update date
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Author user ID
    author = db.relationship('User', backref='projposts')  # Link to user
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))  # Associated project
    milestone_id = db.Column(db.Integer, db.ForeignKey('milestones.oid'))
    milestone = db.relationship('Milestone', back_populates='posts')
    image = db.Column(db.LargeBinary)


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
    

# Association table
team_match = db.Table(
    'team_match',
    db.Model.metadata,
    db.Column('team_id', db.Integer, db.ForeignKey('teams.id'), primary_key=True),
    db.Column('match_id', db.Integer, db.ForeignKey('matches.id'), primary_key=True)
)

# Association table for challenges
team_challenge = db.Table(
    'team_challenge',
    db.Model.metadata,
    db.Column('challenger_id', db.Integer, db.ForeignKey('teams.id'), primary_key=True),
    db.Column('challenged_id', db.Integer, db.ForeignKey('teams.id'), primary_key=True)
)

#team.challenges gives you all teams this team has challenged.
#team.challenged_by gives you all teams that have challenged this team.
#You won’t see challenged_by as a column or explicit attribute in the Team class, but you can use it as a property on any Team instance.

#Example usage:
#team = Team.query.get(1)
#for challenger in team.challenged_by:
#    print(challenger.name)


class Team(db.Model):
    __tablename__ = "teams"
    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer)
    name = db.Column(db.String, unique=True, nullable=False)
    members = db.relationship('User', back_populates='team')
    matches = db.relationship('Match', secondary=team_match, back_populates='teams')
    challenges = db.relationship(
        'Team',
        secondary=team_challenge,
        primaryjoin=id==team_challenge.c.challenger_id,
        secondaryjoin=id==team_challenge.c.challenged_id,
        backref='challenged_by'
    )
    @property
    def rank(self):
        if self.points is None:
            return None  # or some default value
        return Team.query.filter(Team.points > self.points).count() + 1



class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    score_winner = db.Column(db.Integer)
    score_loser = db.Column(db.Integer)
    winner_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    loser_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    teams = db.relationship('Team', secondary=team_match, back_populates='matches')


class GameResult(db.Model):
    __tablename__ = 'game_results'

    id = db.Column(db.Integer, primary_key=True)
    game = db.Column(db.String(50), nullable=False)       # e.g. 'connect4', 'minesweeper'
    winner = db.Column(db.String(50))                     # e.g. 'player1', 'player2', or a label
    score = db.Column(db.Integer)                         # optional numeric score
    played_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship('User', foreign_keys=[user_id], backref='game_results')
    opponent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    opponent = db.relationship('User', foreign_keys=[opponent_id], backref='opponent_game_results')

    def to_dict(self):
        return {
            'id': self.id,
            'game': self.game,
            'winner': self.winner,
            'score': self.score,
            'played_at': self.played_at,
            'user_id': self.user_id,
            'opponent_id': self.opponent_id,
        }