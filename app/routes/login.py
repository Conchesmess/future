
# This file handles login, logout, and user profile features.
# It connects the app to Google for logging in.

from app import app, db, login_manager  # Import app, database, and login manager
from app.classes.data import User  # User model
from app.classes.forms import ProfileForm  # Form for profile image
from datetime import datetime, timezone  # For dates and times
from flask import redirect, flash, request, session, url_for, render_template, abort  # Flask tools
from functools import wraps  # For decorators
from authlib.integrations.flask_client import OAuth  # For Google login
import os  # For environment variables
from flask_login import login_user, current_user, login_required, logout_user  # Login tools
from is_safe_url  import is_safe_url  # Checks if URLs are safe
import requests  # For web requests
from .scopes import scopes  # Google permissions
#import google.oauth2.credentials                
import google_auth_oauthlib.flow                
#import googleapiclient.discovery   
#from oauthlib.oauth2 import WebApplicationClient
#from urllib.parse import urljoin # For handling relative URLs

# Set up Google login
# Google login info

# TODO delete this I think
#GOOGLE_CLIENT_CONFIG = {
#    "web": {
#        "client_id": os.environ['future_google_client_id'],
#        "client_secret": os.environ['future_google_client_id'],
#        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#        "token_uri": "https://oauth2.googleapis.com/token",
#        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#        "redirect_uris": [
#            "https://127.0.0.1:5000/oauth2callback",
#            "https://future-558360858286.us-west1.run.app/oauth2callback",
#            "https://future.ccpa.ninja/oauth2callback"
#        ]
#    }
#}

oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=os.environ['future_google_client_id'],  # Get client ID from secret.py file
    client_secret=os.environ['future_google_secret'],  # Get client secret
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}  # Ask for email and profile info
)

# This function turns Google credentials into a dictionary
def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

@app.after_request
def add_headers(response):
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    return response

@app.before_request
def before_request():

    # Skip HTTPS redirect for local development (127.0.0.1)
    if request.host.startswith('127.0.0.1') or request.host.startswith('localhost'):
        return
    # Check for HTTPS using X-Forwarded-Proto header (for Google Cloud Run)
    forwarded_proto = request.headers.get('X-Forwarded-Proto', 'http')
    if forwarded_proto != 'https':
        url = request.url.replace("http://", "https://", 1)
        code = 301
        return redirect(url, code=code)

def create_or_update_user(user_info):
    """Create or update user in database"""
    thisUser=None
    try:
        # Check if user exists
        thisUser = db.one_or_404(db.select(User).filter_by(google_id=user_info['sub']))
    
    except:
        # Create new user
        if user_info['email'][:1] == "s_":
            thisRole = "student"
        else:
            thisRole = "staff"
        thisUser = User(
            google_id=user_info['sub'],
            email_ousd=user_info['email'],
            fname=user_info['given_name'],
            lname=user_info['family_name'],
            google_image=user_info.get('picture'),
            last_login=datetime.now(timezone.utc),
            role = thisRole
        )
        db.session.add(thisUser)
        flash("Created new user.")
    else:
        # Update existing user
        thisUser.last_login = datetime.now(timezone.utc)
        if thisUser.email_ousd[:1] == 's_' and thisUser.role != "student":
            thisUser.role = 'student'
        else:
            thisUser.role = 'staff'
        flash("Processed existing user.")
    db.session.commit()
    return thisUser
        

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/login')
def login():
    """Initiate Google OAuth login"""
    redirect_uri = url_for('callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@login_manager.user_loader
def load_user(id):
    try:
        user = db.one_or_404(db.select(User).where(User.id == id))
        return user

    except:
        pass


@app.route('/login/callback')
def callback():
    """Handle OAuth callback"""
    try:
        token = google.authorize_access_token()
        current_user.google_id_token = token['id_token']
        user_info = token['userinfo']
        
    except Exception as e:
         flash(f'Login failed: {str(e)}', 'error')
         return redirect(url_for('index'))
    
    else:
        # Create or update user in database
        user = create_or_update_user(user_info)
        login_user(user, force=True)
        load_user(user.id)
        
        flash(f"current user is authenticated: {current_user.is_authenticated}","success")
        #flash(f"Current user has valid google id token: {current_user.is_valid()}","success")

        next = request.args.get('next')
        # url_has_allowed_host_and_scheme should check if the url is safe
        # for redirects, meaning it matches the request host.
        # See Django's url_has_allowed_host_and_scheme for an example.
        if next and is_safe_url(next, request.host):
            return abort(400)
    return redirect(next or url_for('profile'))


@app.route('/profile')
@login_required
def profile():
    #https://teacher.ousd.org/StuPic.ashx?ID=277365&BM=&SC=232&SZ=XLarge
    return render_template('profile.html')

@app.route('/logout')
def logout():
    """Logout user"""
    logout_user()
    if current_user.is_anonymous:
        flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/users')
@login_required
def list_users():
    """Admin page to list all users (for demo purposes)"""
    users = User.query.order_by(User.created_at.desc()).all()
    users_data = [user.to_dict() for user in users]
    
    return render_template('users.html', users=users_data)

@app.route('/valid')
@login_required
def valid():
    if current_user.is_valid():
        flash("Current User has a valid Google Login.","info")
        return redirect(url_for("profile"))
    else:
        flash("Current User needed to refresh Google Credentials.","info")
        return redirect(url_for('login'))


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    form = ProfileForm()
    if form.validate_on_submit():
        if form.image.data:
            current_user.image = form.image.data.read()

        current_user.fname = form.fname.data
        current_user.lname = form.lname.data
        current_user.mobile = form.mobile.data
        current_user.email_personal = form.email_personal.data
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('profile'))
    form.fname.data = current_user.fname
    form.lname.data = current_user.lname
    form.mobile.data = current_user.mobile
    form.email_personal.data = current_user.email_personal
    return render_template('profile_form.html', form=form)
    

@app.route('/authorize')
def authorize():
    # Intiiate login request
    flow = google_auth_oauthlib.flow.Flow.from_client_config(client_config=GOOGLE_CLIENT_CONFIG, scopes=scopes)
    flow.redirect_uri = url_for('callback', _external=True)
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    return redirect(authorization_url)
