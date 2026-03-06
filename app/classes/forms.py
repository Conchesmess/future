
# This file defines forms for the app.
# Forms let users enter information, like stories or profile details.

from flask_wtf import FlaskForm  # Main form class
from wtforms import StringField, SubmitField, TextAreaField, EmailField, FileField, HiddenField, SelectField  # Form fields
from wtforms.validators import InputRequired  # Validator for required fields
# Other validators can be used for more checks

# Form for creating/editing a story
class StoryForm(FlaskForm):
    title = StringField()  # Title of the story
    content = TextAreaField()  # Story content
    image = FileField('Image of the future')  # File upload field
    audio = FileField('Interview Recording')  # File upload field
    audio_base64 = HiddenField('Audio Base64')  # Hidden field for audio in base64
    submit = SubmitField()  # Submit button

# Form for editing user profile
class ProfileForm(FlaskForm):
    fname = StringField()  # First name
    lname = StringField()  # Last name
    email_personal = EmailField()  # Personal email
    mobile = StringField()  # Mobile number
    image = FileField('Profile Image')  # File upload field
    submit = SubmitField()  # Submit button

# Form for uploading a profile image
class ProfileImageForm(FlaskForm):
    image = FileField('Profile Image')  # File upload field
    submit = SubmitField()  # Submit button

