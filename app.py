import markdown 
import pymongo
import secrets
import flask
import json
import time

from flask import Flask, render_template, request, flash, redirect, url_for, session
import markdown.extensions.fenced_code
from passlib.hash import sha256_crypt
import src.LoginRegister as LR

app = Flask(__name__)
secret = secrets.token_urlsafe(32)
app.secret_key = secret

with open('./secret.json') as f:
    data = json.load(f)
mongoPassword = data["MONGO Pass"]
dbURL = "mongodb+srv://admin:" + mongoPassword + "@cluster0.8x8cd.gcp.mongodb.net/TicketedIssues?retryWrites=true&w=majority"
client = pymongo.MongoClient(dbURL)

@app.route('/')
def hello():
    return render_template('hello.html')

@app.route('/docs/', methods=["GET"])
def docs():
    readme_file = open("README.md", "r")
    md_template_string = markdown.markdown(
        readme_file.read(), extensions=["fenced_code"]
    )
    return md_template_string

@app.route('/register/', methods=["GET","POST"])
def register_page():
    try:
        form = LR.RegistrationForm(request.form)
        if request.method == "POST" and form.validate():
            username  = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            userCollection = client["TicketedIssues"]["Users"]
            for users in userCollection.find():
                if users["username"].casefold() == username.casefold():
                    flash("Username is already taken, case-insensitive")
                    return render_template('register.html', form=form)
            else:
                newUser = {
                    "username" : username,
                    "email" : email,
                    "passHash" : password
                }
                userCollection.insert_one(newUser)
                flash("User Registered")
                time.sleep(5)
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('/'))
        return render_template("register.html", form=form)
    except Exception as e:
        return(str(e))

@app.route('/login', methods=['GET', 'POST'])
def login():
    pass

if (__name__ == '__main__'):
    app.run(debug=True)    