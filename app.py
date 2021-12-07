import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///birthdays.db")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Retrieve, add and delete in one POST request"""

    # Render index if there is no POST request
    if request.method == "GET":
        birthdays = db.execute("SELECT * FROM birthdays")
        return render_template("index.html", birthdays = birthdays)

    # Commands to do if there is a POST request
    if request.method == "POST":

        if request.form.get("action") == "submit_delete":
            db.execute( "DELETE FROM birthdays WHERE id = (SELECT MAX(id) FROM birthdays);")

            birthdays = db.execute("SELECT * FROM birthdays")

            return render_template("index.html", birthdays = birthdays)

        # Setting variable for easy usage
        errormessage = " "
        name = request.form.get("name")
        month = request.form.get("month")
        day = request.form.get("day")

        # Setting conditions & display error message
        if not name:
            errormessage = "Name is missing"
            birthdays = db.execute("SELECT * FROM birthdays")
            return render_template("index.html", errormessage = errormessage, birthdays = birthdays)

        elif not month:
            errormessage = "Month is missing"
            birthdays = db.execute("SELECT * FROM birthdays")
            return render_template("index.html", errormessage = errormessage, birthdays = birthdays)


        elif not day:
            errormessage = "Day is missing"
            birthdays = db.execute("SELECT * FROM birthdays")
            return render_template("index.html", errormessage = errormessage, birthdays = birthdays)

        if request.form.get("action") == "submit_add":

            db.execute(
            "INSERT INTO birthdays (name, month, day) VALUES(?, ?, ?)",
            name,
            month,
            day,
            )

        birthdays = db.execute("SELECT * FROM birthdays")

        return render_template("index.html", errormessage = errormessage, birthdays = birthdays)

    else:

        birthdays = db.execute("SELECT * FROM birthdays")

        return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        # Variable pass
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Username must be filled
        if not username:
            return apology("Username is missing")

        # Username must not exist
        elif len(rows) >= 1:
            return apology("Username already exist")

        # Password must be filled
        elif not password:
            return apology("Password is missing")

        # Password confirmation must be filled
        elif not confirmation:
            return apology("Please confirm your password")

        # Password confirmation must match password
        elif not password == confirmation:
            return apology("Password do not match")

        else:
            # Generate password hash
            hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)

            # Add new user to database
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)

            # Redirect to index
            # Imitate alert from staff website
            flash("Registrasion Success!")
            return redirect("/")

    # User reached register via GET
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

# Debug

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

