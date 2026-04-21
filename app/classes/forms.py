
# This file defines forms for the app.
# Forms let users enter information, like stories or profile details.

from flask_wtf import FlaskForm  # Main form class
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, EmailField, FileField, HiddenField, SelectField  # Form fields
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

# Form for creating/editing a project
class ProjectForm(FlaskForm):
    #title = StringField('Title', validators=[InputRequired()])
    name = StringField('Project Name', validators=[InputRequired()])
    description = TextAreaField('Description')
    status = SelectField('Status', choices=[('In Progress', 'In Progress'), ('Completed', 'Completed'), ('On Hold', 'On Hold')])
    milestone = StringField('Milestone')
    course = SelectField('Status', choices=[('CiS6 Enrollment 2026','CiS6 Enrollment 2026')])
    product = TextAreaField('Product')
    learning_materials = TextAreaField('Learning Materials')
    submit = SubmitField('Save Project')

# Form for creating/editing a milestone
class MilestoneForm(FlaskForm):
    name = StringField('Title', validators=[InputRequired()])
    description = TextAreaField('Description')
    due_date = StringField('Due Date')  # Could use DateField if needed
    status = SelectField('Status', choices=[("","--pick one--"),('Not Started', 'Not Started'), ('In Progress', 'In Progress'), ('Completed', 'Completed'),("Delete","Delete")])
    submit = SubmitField('Save Milestone')

# Form for creating/editing a project post
class ProjPostForm(FlaskForm):
    post_type = SelectField('Post Type', choices=[("","--Choose One--"),('Intention', 'Intention'), ('Reflection', 'Reflection'), ('Discussion', 'Discussion')], validators=[InputRequired()])
    confidence = SelectField('Confidence', choices=[(0,"--Pick One--"),(1,"Not"),(2,"Low"),(3,"Dunno"),(4,"Good"),(5,"Fo' Sure")])
    intention = TextAreaField('Intention')
    satisfaction = SelectField('Confidence', choices=[(0,"--Pick One--"),(1,":("),(2,"Cudda been better"),(3,"Meh"),(4,"Pretty good"),(5,"I killed it")])
    reflection = TextAreaField('Reflection')
    discussion = TextAreaField('Discussion')
    milestone = SelectField('Milestone', choices=[])
    image = FileField('Image Reflection')
    submit = SubmitField('Save Post')

# Form for searching posts by date
class SearchDatesForm(FlaskForm):
    start_date = StringField('Start Date', validators=[InputRequired()])
    end_date = StringField('End Date', validators=[InputRequired()])
    submit = SubmitField('Search')

class TeamForm(FlaskForm):
    name = StringField('Team Name', validators=[InputRequired()])
    other_player = SelectField("Other Team Member", choices=[], validate_choice=False)
    submit = SubmitField('Submit')

class TeamChallengeForm(FlaskForm):
    challenged = SelectField("Who do you want to challenge", choices=[], validate_choice=False)
    submit = SubmitField('Submit')

class TeamMatchForm(FlaskForm):
    winner_id = SelectField("Who won?", choices=[], validate_choice=False)
    score_winner = IntegerField("Winner's score")
    loser_id = SelectField("Who lost?", choices=[], validate_choice=False)
    score_loser = IntegerField("Loser's Score")
    submit = SubmitField('Submit')