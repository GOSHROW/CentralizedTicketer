import markdown 
import pymongo
import secrets
import flask
import json
import time
import re

from flask import Flask, render_template, request, flash, redirect, url_for, session, render_template_string, abort, jsonify
import markdown.extensions.fenced_code
from passlib.hash import sha256_crypt
from flask_api import status
import src.LoginRegister as LR
from src.Auth import Auth
from src import Client, Partner

app = Flask(__name__)
secret = secrets.token_urlsafe(32)
app.secret_key = secret
emailRegex = r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"

# Please change these details to your personal MongoDB client
# Within my Cluster on atlas, I have created a DB: "TicketedIssues"
# This encloses the collections: Users and Issues
with open('./secret.json') as f:
    data = json.load(f)
mongoPassword = data["MONGO Pass"]
mongoEndpoint = "@cluster0.8x8cd.gcp.mongodb.net/TicketedIssues?retryWrites=true&w=majority"
dbURL = "mongodb+srv://admin:" + mongoPassword + mongoEndpoint
dbclient = pymongo.MongoClient(dbURL)

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
            password = sha256_crypt.encrypt(str(form.password.data))
            userCollection = dbclient["TicketedIssues"]["Users"]
            if not re.match(emailRegex, email):
                flash("Email Invalid")
                time.sleep(5)
                return redirect(url_for("login"))
            for users in userCollection.find():
                if users["username"].casefold() == username.casefold():
                    flash("Username is already taken, case-insensitive")
                    time.sleep(5)
                    return redirect(url_for("login"))
                if users["email"].casefold() == email.casefold():
                    flash("Email is already taken.")
                    time.sleep(5)
                    return redirect(url_for("login"))
            else:
                newUser = {
                    "username" : username,
                    "email" : email,
                    "passHash" : password, 
                    "auth" : Auth.getAuthVal()
                }
                userCollection.insert_one(newUser)
                flash("User Registered")
                time.sleep(5)
                return redirect(url_for("login"))
        return render_template("register.html", form=form)
    except Exception as e:
        return(str(e))

@app.route('/login/', methods=["GET", "POST"])
def login():
    try:
        # print("A")
        form = LR.LoginForm(request.form)
        if request.method == "POST":
            if form.validate():
                username  = form.username.data
                password = str(form.password.data)
                userCollection = dbclient["TicketedIssues"]["Users"]
                for users in userCollection.find():
                    if users["username"].casefold() == username.casefold():
                        # print("E")
                        isUser = sha256_crypt.verify(password, users["passHash"])
                        print(isUser)
                        if isUser:
                            # print("F")
                            session['logged_in'] = True
                            session['username'] = username
                            return redirect(url_for("auth"))
                        else:
                            # print("G")
                            flash("Error in login.")
                            break
        # print("C")
        return render_template("login.html", form=form)
    except Exception as e:
        return(str(e))

@app.route('/auth/', methods=["GET"])
def getAuth():
    if 'username' in session:
        user = session["username"]
        userCollection = dbclient["TicketedIssues"]["Users"]
        for users in userCollection.find():
            if users["username"] == user:
                return render_template(users["auth"])
        return redirect(url_for("register"))
    else:
        if 'logged_in' not in session or not session["logged_in"]:
            flash("no log in")
            time.sleep(5)
            return redirect(url_for("login"))
        return render_template_string("Error in getting Auth Key, check Session.")


@app.route('/api/client/', methods=["GET", "PUT", "POST", "DELETE"])
def clientMethods():
    if request.method == "GET":
        username = request.args.get('user', '')
        if Client.verify(dbclient, request):
            return Client.getStatus(dbclient, username)
        abort(401)
    if request.method == "PUT":
        if Client.verify(dbclient, request):
            Client.putRequest(dbclient, request)
            return jsonify("SUCCESS"), 200
        abort(401)
    if request.method == "POST":
        if Client.verify(dbclient, request):
            Client.addIssue(dbclient, request)
            return jsonify("SUCCESS"), 200
        abort(401)
    if request.method == "DELETE":
        if Client.verify(dbclient, request):
            Client.delIssue(dbclient, request)
            return jsonify("SUCCESS"), 200
        abort(401)
    abort(400)


@app.route('/api/partner/', methods=["GET", "POST"])
def partnerMethods():  
    if request.method == "GET":
        if Partner.verify(dbclient, request):
            return jsonify(dbclient["TicketedIssues"]["Issues"].find())
        abort(401)
    if request.method == "POST":
        agentname = request.args.get('agent', '')
        key = request.args.get('key', '') 
        issueno =  request.args.get('issueno', '') 
        user = request.args.get('user', '')
        if Partner.verify(dbclient, request):
            dbclient["TicketedIssues"]["Issues"].update({"issueno": issueno, "user": user, "allotted": "None"}, {"allotted": agentname})
            return jsonify("Allotted Success"), 200
        abort(401)
    abort(400)


if (__name__ == '__main__'):
    app.run(debug=True)    