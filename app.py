import os
from conections import Users
from flask import Flask, request, session, render_template
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
user = Users(db)

@app.route("/login")
def logIn():
    return render_template("/login.html", message="")

@app.route("/signUp")
def signUp():
    return render_template("/registration.html")

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        return render_template("/search.html", message="Esto es un post")
    return render_template("/search.html", message="")

@app.route("/signupStatus", methods=["POST"])
def signup_status():
    name = request.form.get("username")
    email = request.form.get("email")
    pwd = request.form.get("password")
    print("FORM REQUEST")
    print(f"Name: {name}, Email: {email}, Pass: {pwd}")
    message = user.insert_user(name,email,pwd)
    return f"<h1> {message} </h1>"
