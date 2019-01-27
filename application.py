import os
import csv

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#A global variable for the current session to track user
current_user=None

@app.route("/")
def index():

    return render_template("index.html")


@app.route("/hello", methods=["POST"])
def hello():
    first = request.form.get("firstName")
    last = request.form.get("lastName")
    ''' This will be saved to the DataBase'''
    return "You typed " + first + " " + last


@app.route("/verify", methods=["POST"])
def verify():
    username = request.form.get("username")
    password = request.form.get("password")

    if password == "password" and username == "username":
        session[username] = True
        return "You are logged in!"

    return "Not registered!"


@app.route("/secret")
def secret():
    for key in session.items():
        print(key)
    if len(session) != 0 and session["username"]:
        return "Secrete Page"
    return "Not logged-in!"


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return "logged out!"
