from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FileField, DateTimeField
from wtforms.validators import DataRequired, Length, EqualTo, URL, Optional
from flask_wtf.file import FileRequired, FileAllowed

class LoginForm(FlaskForm):
    """Form for user login."""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=64)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, max=128)
    ])

class RegistrationForm(FlaskForm):
    """Form for user registration."""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=64)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, max=128)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])

class PostForm(FlaskForm):
    """Form for creating social media posts."""
    platform = SelectField('Platform', validators=[DataRequired()], choices=[
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('pinterest', 'Pinterest'),
        ('tiktok', 'TikTok')
    ])
    media = FileField('Media File', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov'], 'Images and videos only!')
    ])
    caption = TextAreaField('Caption', validators=[Optional(), Length(max=2200)])
    scheduled_time = DateTimeField('Schedule Time', validators=[DataRequired()], format='%Y-%m-%d %H:%M')

class SettingsForm(FlaskForm):
    """Form for configuring API settings."""
    # Facebook
    facebook_access_token = StringField('Facebook Access Token', validators=[Optional()])
    facebook_page_id = StringField('Facebook Page ID', validators=[Optional()])
    
    # Twitter
    twitter_api_key = StringField('Twitter API Key', validators=[Optional()])
    twitter_api_secret = StringField('Twitter API Secret', validators=[Optional()])
    twitter_access_token = StringField('Twitter Access Token', validators=[Optional()])
    twitter_access_token_secret = StringField('Twitter Access Token Secret', validators=[Optional()])
    
    # Instagram
    instagram_access_token = StringField('Instagram Access Token', validators=[Optional()])
    instagram_business_account_id = StringField('Instagram Business Account ID', validators=[Optional()])
    
    # Pinterest
    pinterest_access_token = StringField('Pinterest Access Token', validators=[Optional()])
    pinterest_board_id = StringField('Pinterest Board ID', validators=[Optional()])
    
    # TikTok
    tiktok_access_token = StringField('TikTok Access Token', validators=[Optional()])
    tiktok_open_id = StringField('TikTok Open ID', validators=[Optional()])

class RetryPostForm(FlaskForm):
    """Form for retrying failed posts."""
    post_id = StringField('Post ID', validators=[DataRequired()])

class DeletePostForm(FlaskForm):
    """Form for deleting scheduled posts."""
    post_id = StringField('Post ID', validators=[DataRequired()])

class GenerateCaptionForm(FlaskForm):
    """Form for generating AI captions."""
    image = FileField('Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    platform = SelectField('Platform', validators=[DataRequired()], choices=[
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('pinterest', 'Pinterest'),
        ('tiktok', 'TikTok')
    ])