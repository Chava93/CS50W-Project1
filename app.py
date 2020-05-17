import os
from conections import Users
from flask import Flask, request, redirect, session, render_template
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

@app.route("/signup", methods=["GET","POST"])
def signUp():
    if request.method == "POST":
        ## Agregar usuario nuevo a la tabla users
        name = request.form.get("username")
        email = request.form.get("email")
        pwd = request.form.get("password")
        if not all([name, email, pwd]):
            message = "To register an user, you must enter all fields."
            return render_template("/registration.html",message = message)
        message = user.insert_user(name,email,pwd)
        if "successfully" in message:
            session["user"] = user.getUser(name)
            assert session["user"], "User does not exists"
            return redirect("/")
        return render_template("/registration.html",message = message)

    return render_template("/registration.html")

@app.route("/", methods=["GET","POST"])
def index():
    if "user" not in session.keys():
        return redirect("/login")
    if request.method == "POST":
        return render_template("/search.html", message="Esto es un post")
    return render_template("/search.html", message="")
