from datetime import datetime
from flask import Flask, render_template, current_app, abort, url_for, request, render_template, redirect, session
from flask_mysqldb import MySQL

def home_page():
    return render_template("index.html")

def books_page():
    return render_template("books.html")

def book_page(book_id):
    return render_template("book.html",book_id = book_id)

def authors_page():
    return render_template("authors.html")

def author_page(author_id):
    return render_template("author.html", author_id = author_id)

def register_page():

    if request.method == "GET":
        return render_template("register.html")

    else:
        fullname = request.form["fullname"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        sorgu = "insert into mediaread.user (username, fullName, email, password) values ('"+username+"', '"+fullname+"', '"+email+"', '"+password+"')"
        return redirect(url_for("home_page"))


def login_page():

    if request.method == "GET":
        return render_template("login.html")

    else:
        username = request.form["username"]
        password = request.form["password"]
        session["logged_in"] = True
        session["username"] = username
        return redirect(url_for("home_page"))
    

def logout_page():

    session["logged_in"] = False
    session["username"] = ""
    return redirect(url_for("home_page"))