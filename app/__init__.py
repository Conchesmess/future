
# This file sets up the main app and its features.
# It connects the app to the database, login system, and other tools.
from flask_migrate import Migrate
from flask import Flask, request  # Flask is the main web framework
import os  # Used for environment variables
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData  # For database
from flask_login import LoginManager  # For login/logout
from functools import wraps  # For decorators
from flask_moment import Moment  # For showing dates/times
from markupsafe import Markup  # For safe HTML
from datetime import datetime  # For dates/times
import base64

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = int(64 * 1024 * 1024 * 1.34)  # for 64MB original file
app.config['MAX_FORM_MEMORY_SIZE'] = int(64 * 1024 * 1024 * 1.34)  # for 64MB original file

# Set a secret key for security (change this in real apps!)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# Database setup
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
app.config['SQLALCHEMY_DATABASE_URI'] = ("mysql+pymysql://flaskdb:M0c0s0sness!@/flaskdb?unix_socket=/cloudsql/future-489121:us-west1:flaskdb")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database object
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=naming_convention)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)

# Set up login manager
login_manager = LoginManager(app)
# login_manager = LoginManager()
# login_manager.init_app(app)

# Set up Moment for time display
moment = Moment(app)

# Import modal features for pop-up windows
from app.classes.flaskmodals import Modal, render_template_modal
modal = Modal(app)

# Decorator to confirm deleting items
def confirm_delete(model_class, redirect_url=None, message_fields=[], message_date_field=None):
    """
    This decorator helps confirm deleting things from the database.
    It shows a message before deleting.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ajax = '_ajax' in request.form  # Checks if it's an AJAX request
            if ajax:        # Add these
                return ''   # two lines

            # Get the item ID from route parameters
            item_id = kwargs.get('id')
            if not item_id:
                flash('No item ID provided', 'error')
                return redirect(redirect_url or '/')
            
            # Fetch the item
            item = model_class.query.get_or_404(item_id)
            
            # Check if this is a confirmation request
            if request.method == 'POST' and request.form.get('confirm_delete') == 'true':
                # User confirmed, proceed with deletion
                return f(*args, **kwargs)
            
            # Show confirmation dialog
            display_name=''


            for field in message_fields:
                thisAttribute = getattr(item,field,str(item))
                try:
                    len(thisAttribute)
                except TypeError:
                    pass
                else:
                    thisAttribute = thisAttribute[:100]
                display_name += f"<b> {str(field)}: </b> {thisAttribute} <br>"

            display_name = Markup(display_name)
            try:
                message_date = getattr(item,message_date_field,str(item))
            except:
                message_date=None
            
            return render_template_modal(
                "delete_modal.html",
                item=item,
                display_name=display_name,
                current_url=request.url,
                message_date = message_date,
                cancel_url=redirect_url or request.referrer or '/'
            )
        
        return decorated_function
    return decorator

# function so that Jinja can decode base64 image string that are stored in the DB
def base64encode(img):
    image = base64.b64encode(img)
    image = image.decode('utf-8')
    return image

app.jinja_env.globals.update(base64encode=base64encode)

from .routes import *

@app.after_request
def add_pygbag_isolation_headers(response):
    """Enable SharedArrayBuffer for pygbag games by setting COOP/COEP headers.
    Only applied to /play/ routes and the CDN proxy — not the landing page,
    so the main Flask site nav remains functional behind the popup."""
    path = request.path
    if '/play/' in path or path.startswith('/pygbag-cdn/'):
        response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
        response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    return response
