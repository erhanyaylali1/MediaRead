from flask import Flask, render_template, current_app, abort, url_for, request, render_template, redirect, session, flash
from flask_mysqldb import MySQL
from database import Database
from MySQLdb import IntegrityError

app = Flask(__name__)
app.secret_key = "MediaRead"
db = Database("127.0.0.1", 3307, "root", "3347", "mediaread")
db.check = 0

@app.route('/')
def home_page():

    if session["username"] != "":
        db.cursor.execute("SELECT idUser, fullName from mediaread.user where username = \"" + str(session["username"]) + "\"")
        userInfo = db.cursor.fetchone()
    else:
        userInfo = ""

    return render_template("index.html", userInfo=userInfo)



@app.route('/books', methods = ["GET","POST"])
def books_page():

    if request.method == "GET":

        args = request.args.get("selected_sort")
        print(args)
        db.cursor.execute("SELECT * FROM mediaread.book ORDER BY bookName ASC")
        books = db.cursor.fetchall()
        authors = []
        for i in range (len(books)):

            db.cursor.execute("SELECT idAuthor, fullName FROM mediaread.author where idAuthor = " + str(books[i][7]))
            authors.append(db.cursor.fetchone())
        
        return render_template("books.html", books=books, authors=authors, len=len(books))    
    
    else:
        bookId = request.form["bookId"]
        ids = bookId.split("-")

        if session["logged_in"]:
            userId = session["userId"]
            bookId = ids[0]
            authorId = ids[1]
            sorgu = "INSERT INTO mediaread.user_has_book (user_id, book_id, author_id) values (" + str(userId) + ", " + str(bookId) + ", " + str(authorId) + ")"
            
            try:
                db.cursor.execute(sorgu)
                db.con.commit()
                flash("You added this book in your library","success")

            except IntegrityError:
                flash("You already have this book in your library","danger")

        return redirect(url_for("books_page"))



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
        db.cursor.execute("SELECT * FROM mediaread.category")
        categories = db.cursor.fetchall()
        db.cursor.execute("SELECT COUNT(idCategory) FROM mediaread.category")
        lengthCategory = db.cursor.fetchone();

        return render_template("author.html", author_id = author_id, author=author, books=books, categories=categories, length=lengthCategory[0])

    else:

        fullname = request.form["title"]
        page = request.form["page"]
        publisher = request.form["publisher"]
        summary = request.form["summary"]
        image = request.form["image"]
        categories = request.form.getlist("cat")

        if fullname and summary and image and publisher and page and categories:
            sorgu = "insert into mediaread.book (bookName, pageNumber, publisher, summaryBook, bookImage, author_id) values (\""+ fullname +"\", \""+page+"\", \""+publisher+"\", \""+summary+"\", \""+image+"\", \""+str(author_id)+"\")"
            db.cursor.execute(sorgu)
            db.con.commit()
            sorgu = "select idbook from mediaread.book where author_id = " + str(author_id) + " AND bookName = \"" + fullname + "\" AND pageNumber = " + str(page)
            db.cursor.execute(sorgu)
            bookId = db.cursor.fetchone()
            bookId = bookId[0]
            print(bookId)

            for cat in categories:
                sorgu = "insert into mediaread.book_has_category (book_id, author_id, category_id) values ("+str(bookId)+","+str(author_id)+","+str(cat)+")"
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



@app.route('/categories')
def categories_page():

    sorgu = "select * from mediaread.category"
    db.cursor.execute(sorgu)
    categories = db.cursor.fetchall()
    return render_template("categories.html", categories=categories)
    


@app.route('/categories/<int:category_id>')
def category_page(category_id):

    sorgu = "select book_id from mediaread.book_has_category where category_id = " + str(category_id)
    db.cursor.execute(sorgu)
    book_ids = db.cursor.fetchall()
    sorgu2 = "select categoryName from mediaread.category where idCategory = " + str(category_id)
    db.cursor.execute(sorgu2)
    categoryName = db.cursor.fetchone()
    category = categoryName[0]
    books = []
    authors = []

    for book_id in book_ids:
        
        sorgu3 = "select * from mediaread.book where idBook = " + str(book_id[0])
        db.cursor.execute(sorgu3)
        bookInfos = db.cursor.fetchone()
        books.append(bookInfos)
        sorgu4 = "select fullName from mediaread.author where idAuthor = " + str(bookInfos[7])
        db.cursor.execute(sorgu4)
        authorName = db.cursor.fetchone()
        authors.append(authorName)

    length = len(books)
    return render_template("category.html", books=books, authors=authors, length=length, category=category)



@app.route('/users/<int:user_id>/myLibrary')
def library_page(user_id):

    sorgu = "select * from mediaread.user_has_book where user_id = " + str(user_id)
    db.cursor.execute(sorgu)
    ids = db.cursor.fetchall()
    books = []
    authors = []

    for idx in ids:

        sorgu2 = "select * from mediaread.book where idBook = " + str(idx[1])
        db.cursor.execute(sorgu2)
        books.append(db.cursor.fetchone())
        sorgu3 = "select * from mediaread.author where idAuthor = " + str(idx[2])
        db.cursor.execute(sorgu3)
        authors.append(db.cursor.fetchone())

    length = len(books)
    return render_template("library.html", books=books, authors=authors, length=length)



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

            sorgu = "select password, idUser from mediaread.user where username = \"" + username + "\""
            
            db.cursor.execute(sorgu)
            check = db.cursor.fetchone()
            
            if check:

                if check[0] == password:
                    session["logged_in"] = True
                    session["username"] = username
                    session["userId"] = check[1]
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
    session["userId"] = ""
    flash("LOGGED OUT SUCCESSFULLY","success")
    return redirect(url_for("home_page"))



if __name__ == '__main__':
    app.run(debug=True)
