from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField


### Creating a forms

# Blogpost Form
class BlogForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle of the Blog", validators=[DataRequired()])
    img_url = StringField("Blog image")
    body = CKEditorField("Blog content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# Registration Form
class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")


# Login Form
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


# Comment Form
class CommentForm(FlaskForm):
    comment = StringField("Write comment")
    submit = SubmitField("Comment")

