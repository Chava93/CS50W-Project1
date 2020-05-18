import os
from flask import Flask, request, redirect, session, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
## LOCAL LIBRARIES ##
from conections import Users, Books, Reviews

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
books = Books(db)
reviews = Reviews(db)

@app.route("/login", methods=["GET","POST"])
def logIn():
    if request.method == "POST":
        # name may be an user or username
        name = request.form.get("username")
        pwd = request.form.get("password")
        ## Look user as username
        userinfo, message = user.validateUser(name, pwd)
        if userinfo:
            session["user"] = userinfo
            return redirect("/")
        ## If not found
        return render_template("/login.html", message="User and username not Found.")
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
    print(f"logged with user: {session['user']}")
    if request.method == "POST":
        query_info = {
            "isbn": request.form.get("isbn"),
            "title": request.form.get("book"),
            "author": request.form.get("author"),
        }
        info, message = books.get_book(query_info)
        return render_template("/search.html", message=message, books=info)
    return render_template("/search.html", message="")

@app.route("/logout", methods=["GET"])
def logout():
    del session["user"]
    return redirect("/login")

@app.route("/books/<string:isbn>", methods=["GET","POST"])
def book_reviews(isbn):
    if "user" not in session.keys():
        return redirect("/login")
    if request.method == "POST":
        review_info = {
            "review": request.form.get("review"),
            "rating": request.form.get("rating")
        }
        if review_info["review"]:
            user = session["user"]["user"]
            reviews.insert_review(user, isbn, review_info)
    review, rev_message = reviews.get_review({"isbn":isbn})
    book,message = books.get_book({"isbn":isbn})
    print(review)
    if not book:
        return message
    return render_template("book.html", book = book[0], reviews=review)
