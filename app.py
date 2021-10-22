import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///birthdays.db")

@app.route("/", methods=["GET", "POST"])
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


