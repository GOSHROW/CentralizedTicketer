from wtforms import Form, BooleanField, TextField, PasswordField, validators

class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address')
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I have ensured that my Password is unique and its leak or its hash\'s leak is not a concern of the provider: GOSHROW', [validators.Required()])
    # TODO: Got to work on ensuring safetyy

class LoginForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    password = PasswordField('Enter Password')