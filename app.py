from flask import Flask, render_template, current_app, abort, url_for, request, render_template, redirect, session, flash
from flask_mysqldb import MySQL
from database import Database

app = Flask(__name__)
app.secret_key = "MediaRead"
db = Database("127.0.0.1", 3307, "root", "3347", "mediaread")

@app.route('/')
def home_page():
    return render_template("index.html")

@app.route('/books')
def books_page():

    db.cursor.execute("SELECT * FROM mediaread.book")
    books = db.cursor.fetchall()
    authors = []
    for i in range (len(books)):

        db.cursor.execute("SELECT idAuthor, fullName FROM mediaread.author where idAuthor = " + str(books[i][7]))
        authors.append(db.cursor.fetchone())
    
    return render_template("books.html", books=books, authors=authors, len=len(books))    

@app.route('/books/<int:book_id>')
def book_page(book_id):
    db.cursor.execute("SELECT * FROM mediaread.book where idBook = " + str(book_id))
    book = db.cursor.fetchone()
    db.cursor.execute("SELECT idAuthor, fullName FROM mediaread.author where idAuthor = " + str(book[7]))
    author = db.cursor.fetchone()
    db.cursor.execute("SELECT category_id FROM mediaread.book_has_category where book_id = " + str(book_id))
    categoryIds = db.cursor.fetchall()
    categories = []
    for i in range(len(categoryIds)):
        db.cursor.execute("SELECT * FROM mediaread.category where idCategory = " + str(categoryIds[i][0]))
        categories.append(db.cursor.fetchone())

    return render_template("book.html",book_id = book_id, book=book, author=author, categories=categories)


@app.route('/authors')
def authors_page():
    db.cursor.execute("SELECT * FROM mediaread.author")
    authors = db.cursor.fetchall()
    return render_template("authors.html",authors=authors)


@app.route('/authors/<int:author_id>')
def author_page(author_id):
    db.cursor.execute("SELECT * FROM mediaread.author where idAuthor = " + str(author_id))
    author = db.cursor.fetchone()
    db.cursor.execute("SELECT * FROM mediaread.book where author_id = " + str(author_id))
    books = db.cursor.fetchall()
    return render_template("author.html", author_id = author_id, author=author, books=books)

@app.route('/register', methods = ["GET","POST"])
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


@app.route('/login', methods = ["GET","POST"])
def login_page():

    if request.method == "GET":
        return render_template("login.html")

    else:
        username = request.form["username"]
        password = request.form["password"]
        session["logged_in"] = True
        session["username"] = username
        return redirect(url_for("home_page"))


@app.route('/logout')
def logout_page():

    session["logged_in"] = False
    session["username"] = ""
    return redirect(url_for("home_page"))



if __name__ == '__main__':
    app.run(debug=True)
