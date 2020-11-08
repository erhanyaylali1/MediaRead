from flask import Flask, render_template, current_app, abort, url_for, request, render_template, redirect, session, flash
from flask_mysqldb import MySQL
from database import Database

app = Flask(__name__)
app.secret_key = "MediaRead"
db = Database("127.0.0.1", 3307, "root", "3347", "mediaread")

@app.route('/')
def home_page():

    if session["username"] != "":
        db.cursor.execute("SELECT idUser, fullName from mediaread.user where username = \"" + str(session["username"]) + "\"")
        userInfo = db.cursor.fetchone()
    
    else:
        userInfo = ""

    return render_template("index.html", userInfo=userInfo)

@app.route('/books')
def books_page():

    db.cursor.execute("SELECT * FROM mediaread.book ORDER BY bookName ASC")
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
    length = len(authors)
    booksNum = []
    for i in range(len(authors)):
        db.cursor.execute("SELECT COUNT(bookName) FROM mediaread.book where author_id = " + str(authors[i][0]))
        booksNum.append(db.cursor.fetchone())

    return render_template("authors.html",authors=authors, length=length, booksNum=booksNum)


@app.route('/authors/<int:author_id>', methods = ["GET","POST"])
def author_page(author_id):

    if request.method == "GET":

        db.cursor.execute("SELECT * FROM mediaread.author where idAuthor = " + str(author_id))
        author = db.cursor.fetchone()
        db.cursor.execute("SELECT * FROM mediaread.book where author_id = " + str(author_id))
        books = db.cursor.fetchall()
        return render_template("author.html", author_id = author_id, author=author, books=books)

    else:

        fullname = request.form["title"]
        page = request.form["page"]
        publisher = request.form["publisher"]
        summary = request.form["summary"]
        image = request.form["image"]

        if fullname and summary and image and publisher and page:
            sorgu = "insert into mediaread.book (bookName, pageNumber, publisher, summaryBook, bookImage, author_id) values (\""+ fullname +"\", \""+page+"\", \""+publisher+"\", \""+summary+"\", \""+image+"\", \""+str(author_id)+"\")"
            print(sorgu)
            db.cursor.execute(sorgu)
            db.con.commit()
            flash("BOOK ADDED SUCCESSFULLY","success")
            
        return redirect(url_for("author_page",author_id=author_id))


@app.route('/addAuthor', methods = ["GET","POST"])
def add_author_page():

    if request.method == "GET":
        return render_template("addAuthor.html")
    
    else:
        fullname = request.form["fullname"]
        summary = request.form["summary"]
        image = request.form["image"]

        if fullname and summary and image:
            sorgu = "insert into mediaread.author (fullName, summaryAuthor, authorImage) values (\""+fullname+"\", \""+summary+"\", \""+image+"\")"
            db.cursor.execute(sorgu)
            db.con.commit()
            flash("AUTHOR ADDED SUCCESSFULLY","success")
        return redirect(url_for("authors_page"))

    

@app.route('/register', methods = ["GET","POST"])
def register_page():

    if request.method == "GET":
        return render_template("register.html")

    else:
        fullname = request.form["fullname"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]

        if fullname and email and username and password:
            sorgu = "insert into mediaread.user (username, fullName, email, password) values (\""+username+"\", \""+fullname+"\", \""+email+"\", \""+password+"\")"
            db.cursor.execute(sorgu)
            db.con.commit()
            flash("REGISTERED SUCCESSFULLY","success")

        return redirect(url_for("login_page"))


@app.route('/login', methods = ["GET","POST"])
def login_page():

    if request.method == "GET":
        return render_template("login.html")

    else:
        username = request.form["username"]
        password = request.form["password"]

        if username and password:

            sorgu = "select password from mediaread.user where username = \"" + username + "\""
            
            db.cursor.execute(sorgu)
            check = db.cursor.fetchone()
            
            if check:

                if check[0] == password:
                    session["logged_in"] = True
                    session["username"] = username
                    flash("LOGGED IN SUCCESSFULLY","success")
                    return redirect(url_for("home_page"))

                else:
                    flash("WRONG PASSWORD","danger")

            else:
                flash("WRONG USERNAME","danger")
                
        return redirect(url_for("login_page"))


@app.route('/logout')
def logout_page():

    session["logged_in"] = False
    session["username"] = ""
    flash("LOGGED OUT SUCCESSFULLY","success")
    return redirect(url_for("home_page"))



if __name__ == '__main__':
    app.run(debug=True)
