from flask import Flask, render_template, current_app, abort, url_for, request, render_template, redirect, session, flash, jsonify
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from database import Database
from operator import itemgetter
import mysql.connector
from passlib.hash import sha256_crypt


app = Flask(__name__)
app.secret_key = "MediaRead"
db = Database("127.0.0.1", "root", "3347", "mediaread")
db.check = 0


@app.route('/')
def home_page():

    userInfo = ""
    if "username" in session:

        db.cursor.execute("SELECT idUser, fullName from mediaread.user where username = \"" + str(session["username"]) + "\"")
        userInfo = db.cursor.fetchone()

        sorgu = """
            SELECT mediaread.user_review_book.time, mediaread.user_review_book.review, mediaread.user.fullName, mediaread.user.idUser,
            mediaread.book.idbook, mediaread.book.bookName, mediaread.author.idAuthor, mediaread.user_review_book.rate, mediaread.author.fullName
            FROM mediaread.user_has_friend
            LEFT JOIN mediaread.user
            ON mediaread.user.idUser = mediaread.user_has_friend.friendId
            LEFT JOIN mediaread.user_review_book
            ON mediaread.user.idUser = mediaread.user_review_book.user_id
            LEFT JOIN mediaread.book
            ON mediaread.user_review_book.book_id = mediaread.book.idbook
            LEFT JOIN mediaread.author
            ON mediaread.user_review_book.author_id = mediaread.author.idAuthor
            WHERE mediaread.user_has_friend.userId = """ + str(session["userId"]) + """
            ORDER BY mediaread.user_review_book.time DESC
            """

        db.cursor.execute(sorgu)
        reviews = db.cursor.fetchall()

        sorgu = """
            SELECT mediaread.quote.time, mediaread.quote.quoteContent, mediaread.user.fullName,
            mediaread.user.idUser, mediaread.book.idbook, mediaread.book.bookName, mediaread.author.idAuthor, mediaread.author.fullName
            FROM mediaread.user_has_friend
            LEFT JOIN mediaread.user
            ON mediaread.user.idUser = mediaread.user_has_friend.friendId
            LEFT JOIN mediaread.quote
            ON mediaread.user.idUser = mediaread.quote.user_id
            LEFT JOIN mediaread.book
            ON mediaread.quote.book_id = mediaread.book.idbook
            LEFT JOIN mediaread.author
            ON mediaread.quote.author_id = mediaread.author.idAuthor
            WHERE mediaread.user_has_friend.userId = """ + str(session["userId"]) + """
            ORDER BY mediaread.quote.time DESC
            """

        db.cursor.execute(sorgu)
        quotes = db.cursor.fetchall()
        final = reviews + quotes
        filter(None, final)

        final = [x for x in final if x[0] != None]

        final.sort(key = lambda x: x[0], reverse=True)
        length = len(final)
        ayr = []

        for i in final:
            if len(i) == 8:
                ayr.append(1)
            else:
                ayr.append(0)

    else:

        userInfo = ""
        final = 0
        ayr = 0
        length = 0

    sorgu = """
        select mediaread.user_read_book.author_id, mediaread.author.fullName
        from  mediaread.user_read_book
        LEFT JOIN mediaread.book
        ON mediaread.user_read_book.book_id = mediaread.book.idbook
        LEFT JOIN mediaread.author
        ON mediaread.book.author_id = mediaread.author.idAuthor
        where mediaread.user_read_book.time >= DATE_SUB(NOW(),INTERVAL 1 MONTH)
        group by mediaread.user_read_book.author_id
        limit 1
    """
    db.cursor.execute(sorgu)
    auth = db.cursor.fetchone()

    sorgu = """
        select mediaread.user_read_book.book_id,mediaread.book.bookName
        from  mediaread.user_read_book
        LEFT JOIN mediaread.book
        ON mediaread.user_read_book.book_id = mediaread.book.idbook
        LEFT JOIN mediaread.author
        ON mediaread.book.author_id = mediaread.author.idAuthor
        where mediaread.user_read_book.time >= DATE_SUB(NOW(),INTERVAL 1 MONTH)
        group by mediaread.user_read_book.book_id
		limit 1
    """
    db.cursor.execute(sorgu)
    book = db.cursor.fetchone()

    return render_template("index.html", userInfo=userInfo, final=final, ayr=ayr, length=length, book=book, auth=auth)



@app.route("/livesearch",methods=["POST","GET"])
def livesearch():

    key = request.form.get("text")
    sorgu = """
    SELECT mediaread.book.idbook, mediaread.book.bookName, mediaread.book.bookImage, 0 FROM mediaread.book
    WHERE mediaread.book.bookName LIKE '%"""+key+"""%'
    UNION
    SELECT mediaread.author.idAuthor,mediaread.author.fullName,mediaread.author.authorImage, 1 FROM mediaread.author
    WHERE mediaread.author.fullName LIKE '%"""+key+"""%'
    UNION
    SELECT mediaread.user.idUser,mediaread.user.fullName,mediaread.user.username, 2 FROM mediaread.user
    WHERE mediaread.user.fullName LIKE '%"""+key+"""%'
    limit 10
    """
    db.cursor.execute(sorgu)
    results = db.cursor.fetchall()

    return jsonify(results)



@app.route("/getlogged", methods=["POST","GET"])
def getlogged():
    x = 0
    if "logged_in" in session:
        if session["logged_in"] == True:
            x = 1
    return jsonify(x);



@app.route("/getnotification", methods=["POST","GET"])
def getnotification():

    results = []

    if "userId" in session:
        sorgu = """
        SELECT mediaread.user_has_friend.flag, mediaread.user.fullName, mediaread.user.idUser
        FROM mediaread.user_has_friend
        LEFT JOIN mediaread.user
        ON mediaread.user_has_friend.userId = mediaread.user.idUser
        WHERE mediaread.user_has_friend.friendId = """ + str(session["userId"]) + " ORDER BY mediaread.user_has_friend.time DESC"
        db.cursor.execute(sorgu)
        results = db.cursor.fetchall()

    return jsonify(results)



@app.route("/readnotification", methods=["POST","GET"])
def readnotification():

    keys = request.form.getlist("text[]")
    for key in keys:
        sorgu = """
            UPDATE mediaread.user_has_friend SET mediaread.user_has_friend.flag = 1
            WHERE mediaread.user_has_friend.userId = """+str(key)+""" and mediaread.user_has_friend.friendId = """+str(session["userId"])
        db.cursor.execute(sorgu)
        db.con.commit()



    return "true"



@app.route('/books', methods = ["GET","POST"])
def books_page():

    if request.method == "GET":

        sort = request.args.get('sort')

        if sort == 'book_a':
            db.cursor.execute("SELECT * FROM mediaread.book LEFT JOIN mediaread.author ON mediaread.book.author_id = mediaread.author.idAuthor ORDER BY mediaread.book.bookName ASC")
        elif sort == 'book_d':
            db.cursor.execute("SELECT * FROM mediaread.book LEFT JOIN mediaread.author ON mediaread.book.author_id = mediaread.author.idAuthor ORDER BY mediaread.book.bookName DESC")
        elif sort == 'author_a':
            db.cursor.execute("SELECT * FROM mediaread.book LEFT JOIN mediaread.author ON mediaread.book.author_id = mediaread.author.idAuthor ORDER BY mediaread.author.fullName ASC")
        elif sort == 'author_d':
            db.cursor.execute("SELECT * FROM mediaread.book LEFT JOIN mediaread.author ON mediaread.book.author_id = mediaread.author.idAuthor ORDER BY mediaread.author.fullName DESC")
        elif sort == 'rate_a':
            db.cursor.execute("SELECT * FROM mediaread.book LEFT JOIN mediaread.author ON mediaread.book.author_id = mediaread.author.idAuthor ORDER BY mediaread.book.rate ASC")
        elif sort == 'rate_d':
            db.cursor.execute("SELECT * FROM mediaread.book LEFT JOIN mediaread.author ON mediaread.book.author_id = mediaread.author.idAuthor ORDER BY mediaread.book.rate DESC")
        else:
            db.cursor.execute("SELECT * FROM mediaread.book LEFT JOIN mediaread.author ON mediaread.book.author_id = mediaread.author.idAuthor")

        allData = db.cursor.fetchall()
        length = len(allData)


        readlists = ""
        if "logged_in" in session and session["logged_in"]:
            userId = session["userId"]
            sorgu = """
                SELECT *
                FROM mediaread.user_has_readlist
                LEFT JOIN mediaread.readlist
                ON mediaread.user_has_readlist.readlist_idreadlist = mediaread.readlist.idreadlist
                WHERE mediaread.user_has_readlist.user_idUser =
            """
            db.cursor.execute(sorgu+str(userId)+" GROUP BY mediaread.user_has_readlist.readlist_idreadlist")
            readlists = db.cursor.fetchall()


        return render_template("books.html", allData=allData, length=length, readlists=readlists)

    else:


        bookId = request.form.get("bookId")
        readlistId = request.form.getlist("readlist")
        saved = request.form.get("savedbook")
        if bookId is not None:

            ids = bookId.split("-")
            userId = session["userId"]

            if session["logged_in"]:
                bookId = ids[0]
                authorId = ids[1]
                sorgu = "INSERT INTO mediaread.user_has_book (user_id, book_id, author_id) values (" + str(userId) + ", " + str(bookId) + ", " + str(authorId) + ")"

                try:
                    db.cursor.execute(sorgu)
                    db.con.commit()

                    flash("You added this book in your library","success")

                except mysql.connector.Error:
                    flash("You already have this book in your library","danger")


            return redirect(url_for("books_page"))

        if readlistId is not None:

            userId = session["userId"]
            for readId in readlistId:
                ids = readId.split("-")
                bookId = ids[0]
                authorId = ids[1]
                readlistId = ids[2]

                try:
                    sorgu = "INSERT INTO mediaread.user_has_readlist (user_idUser, readlist_idreadlist, book_idbook, book_author_id) VALUES ("+str(userId)+","+str(readlistId)+","+str(bookId)+","+str(authorId)+")"
                    db.cursor.execute(sorgu)
                    db.con.commit()

                    flash("You added this book in your readlist","success")

                except mysql.connector.Error:
                    flash("You already have this book in your readlist","danger")


            return redirect(url_for("readlist_page",user_id=userId,readlist_id=readlistId))



@app.route('/books/<int:book_id>', methods = ["GET","POST"])
def book_page(book_id):

    if request.method == "GET":
        sorgu = """
            SELECT * FROM mediaread.book
            LEFT JOIN mediaread.author
            ON mediaread.book.author_id = mediaread.author.idAuthor
            LEFT JOIN mediaread.book_has_category
            ON mediaread.book.idbook=mediaread.book_has_category.book_id
            LEFT JOIN mediaread.category
            ON mediaread.book_has_category.category_id=mediaread.category.idCategory
            WHERE mediaread.book.idbook =
        """
        db.cursor.execute(sorgu + str(book_id))
        book = db.cursor.fetchall()
        sorgu = """
            SELECT *
            FROM mediaread.book
            LEFT JOIN mediaread.user_review_book
            ON mediaread.user_review_book.book_id = mediaread.book.idbook
            LEFT JOIN mediaread.user
            ON mediaread.user_review_book.user_id = mediaread.user.idUser
            WHERE mediaread.book.idbook =
        """
        db.cursor.execute(sorgu + str(book_id) + " ORDER BY mediaread.user_review_book.time DESC")
        reviews = db.cursor.fetchall()
        check2 = 0
        if reviews[0][9] is None:
            check2 = 1

        sorgu = """
            SELECT *
            FROM mediaread.book
            LEFT JOIN mediaread.quote
            ON mediaread.book.idbook = mediaread.quote.book_id
            LEFT JOIN mediaread.user
            ON mediaread.quote.user_id = mediaread.user.idUser
            WHERE mediaread.book.idbook =
        """

        db.cursor.execute(sorgu + str(book_id) + " ORDER BY mediaread.quote.time DESC")
        quotes = db.cursor.fetchall()
        check = 0
        if quotes[0][9] is None:
            check = 1


        return render_template("book.html",book=book, reviews=reviews, quotes=quotes, check=check, check2=check2)

    else:

        quoteVal = request.form.get("addQuoteButton")
        quote = request.form.get("quote")
        reviewVal = request.form.get("addReviewButton")
        review = request.form.get("review")
        rate = request.form.get("rate")
        savedbook = request.form.get("savedbook")
        addtolibrary = request.form.get("addToLibraryfromBook")

        if reviewVal is not None:
            reviewVal = reviewVal.split("-")
            user_id = reviewVal[0]
            author_id = reviewVal[1]
            try:
                sorgu = "INSERT INTO mediaread.user_review_book (review, rate, user_id, book_id, author_id,time) VALUES (\""+review+"\","+rate+","+str(user_id)+","+str(book_id)+","+str(author_id)+",current_timestamp())"

                db.cursor.execute(sorgu)
                db.con.commit()

                sorgu = "SELECT rate,readNumber from mediaread.book where idbook = " + str(book_id)
                db.cursor.execute(sorgu)
                comings = db.cursor.fetchone()
                rateOld = comings[0]
                readNumber = comings[1]
                newRate = (rateOld * readNumber + int(rate)) / (readNumber + 1)
                sorgu = "UPDATE mediaread.book SET rate = "+ str(newRate)+" where idBook = "+str(book_id)
                db.cursor.execute(sorgu)
                db.con.commit()

                flash("You succesfully gave a review to this book","success")

            except mysql.connector.Error:
                flash("You already gave a review to this book","danger")


        else:

            if quoteVal is not None:

                quote = quote.replace('"',"'")
                quoteVal = quoteVal.split("-")
                user_id = quoteVal[0]
                author_id = quoteVal[1]
                sorgu = "INSERT INTO mediaread.quote (quoteContent, user_id, book_id, author_id, time) VALUES (\""+quote+"\","+str(user_id)+","+str(book_id)+","+str(author_id)+",current_timestamp())"

                db.cursor.execute(sorgu)
                db.con.commit()

            elif addtolibrary is not None:

                userid = session["userId"]
                ids = addtolibrary.split("-")
                authorId = ids[0]
                bookdId = ids[1]

                try:
                    sorgu = "INSERT INTO mediaread.user_has_book (user_id, book_id, author_id) VALUES ("+str(userid)+","+str(bookdId)+","+authorId+")"
                    db.cursor.execute(sorgu)
                    db.con.commit()
                    flash("You added This Book to Your Library Succesfully","success")

                except mysql.connector.Error:
                    flash("You Already Have This Book in your Library","danger")


            else:

                if savedbook is not None:

                    userid = session["userId"]

                    try:
                        sorgu = "INSERT INTO mediaread.user_saved_book (user_id, book_id) VALUES("+str(userid)+","+str(book_id)+")"
                        db.cursor.execute(sorgu)
                        db.con.commit()

                        flash("You added this book in Saved Books Page","success")

                    except mysql.connector.Error:
                        flash("You already have this book in Saved Books Page","danger")



        return redirect(request.url)



@app.route('/authors')
def authors_page():

    db.cursor.execute("SELECT mediaread.author.idAuthor, mediaread.author.fullName, mediaread.author.authorImage, COUNT(mediaread.book.author_id) FROM mediaread.author LEFT JOIN mediaread.book ON mediaread.author.idAuthor = mediaread.book.author_id group by mediaread.author.idAuthor")
    authors = db.cursor.fetchall()
    length = len(authors)

    return render_template("authors.html",authors=authors, length=length)



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
        lengthCategory = db.cursor.fetchone()


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

    sorgu = """
        SELECT * FROM mediaread.category
        LEFT JOIN mediaread.book_has_category
        ON mediaread.category.idCategory = mediaread.book_has_category.category_id
        LEFT JOIN mediaread.book
        ON mediaread.book_has_category.book_id = mediaread.book.idbook
        LEFT JOIN mediaread.author
        ON mediaread.book.author_id = mediaread.author.idAuthor
        WHERE mediaread.category.idCategory =
    """
    sorgu = sorgu + str(category_id)
    db.cursor.execute(sorgu)
    datas = db.cursor.fetchall()
    length = len(datas)

    return render_template("category.html", datas=datas, length=length)



@app.route('/users/<int:user_id>/myLibrary', methods = ["GET","POST"])
def library_page(user_id):

    if request.method == "GET":

        sort = request.args.get('sort')
        sorgu = """
            SELECT * FROM mediaread.user_has_book
            LEFT JOIN mediaread.book
            ON mediaread.user_has_book.book_id = mediaread.book.idbook
            LEFT JOIN mediaread.author
            ON mediaread.book.author_id = mediaread.author.idAuthor
            LEFT JOIN mediaread.user
            ON mediaread.user_has_book.user_id = mediaread.user.idUser
            WHERE mediaread.user.idUser =
        """

        sorgu = sorgu + str(user_id)
        if sort == 'book_a':
            sorgu = sorgu + " ORDER BY mediaread.book.bookName ASC"
        elif sort == 'book_d':
            sorgu = sorgu + " ORDER BY mediaread.book.bookName DESC"
        elif sort == 'author_a':
            sorgu = sorgu + " ORDER BY mediaread.author.fullName ASC"
        elif sort == 'author_d':
            sorgu = sorgu + " ORDER BY mediaread.author.fullName DESC"
        elif sort == 'rate_a':
            sorgu = sorgu + " ORDER BY mediaread.book.rate ASC"
        elif sort == 'rate_d':
            sorgu = sorgu + " ORDER BY mediaread.book.rate DESC"

        db.cursor.execute(sorgu)
        datas = db.cursor.fetchall()
        length = len(datas)

        sorgu = """
                SELECT *
                FROM mediaread.user_has_readlist
                LEFT JOIN mediaread.readlist
                ON mediaread.user_has_readlist.readlist_idreadlist = mediaread.readlist.idreadlist
                WHERE mediaread.user_has_readlist.user_idUser =
            """
        db.cursor.execute(sorgu+str(user_id)+" GROUP BY mediaread.user_has_readlist.readlist_idreadlist")
        readlists = db.cursor.fetchall()


        return render_template("library.html", datas=datas, length=length,readlists=readlists)

    else:

        bookId = request.form.get("bookId")
        rate = request.form.get("rate")
        review = request.form.get("review")
        idler = request.form.get("bookauthor_id")
        userId = user_id
        readlistId = request.form.getlist("readlist")

        if bookId is not None:

            ids = bookId.split("-")
            bookId = ids[0]
            authorId = ids[1]
            sorgu = "DELETE FROM mediaread.user_has_book WHERE user_id = " + str(userId) + " AND book_id = " + str(bookId) + " AND author_id = " + str(authorId)

            db.cursor.execute(sorgu)
            db.con.commit()
            flash("You've delete this book in your library","success")


            return redirect(request.url)

        if idler is not None:

            ids = idler.split("-")
            bookId = ids[0]
            authorId = ids[1]

            try:
                sorgu4 = "INSERT INTO mediaread.user_read_book (user_id, book_id, author_id, time) VALUES ("+str(userId)+", "+str(bookId)+", "+str(authorId)+",current_timestamp())"
                db.cursor.execute(sorgu4)
                db.con.commit()
                flash("You added this book to Read Books Page","success")

                sorgu = "INSERT INTO mediaread.user_review_book (review, rate, user_id, book_id, author_id, time) VALUES (\""+review+"\","+str(rate)+","+str(userId)+","+str(bookId)+","+str(authorId)+",current_timestamp())"
                db.cursor.execute(sorgu)
                db.con.commit()

                sorgu2 = "SELECT * FROM mediaread.book where mediaread.book.idbook = " + str(bookId)
                db.cursor.execute(sorgu2)
                datas = db.cursor.fetchone()

                readNum = datas[8]
                rateOld = datas[5]
                readNum += 1
                rateNew = ( rateOld * (readNum - 1) + int(rate) ) / readNum

                sorgu3 = "UPDATE mediaread.book SET rate="+str(rateNew)+", readNumber="+str(readNum)+" where mediaread.book.idbook = "+bookId
                db.cursor.execute(sorgu3)
                db.con.commit()

                flash("You added this book to Read Books Page","success")

            except mysql.connector.Error:
                    flash("You already have this book in Read Books Page","danger")


            return redirect(url_for("readbook_page",user_id=userId))

        if readlistId is not None:


            userId = session["userId"]
            for readId in readlistId:
                ids = readId.split("-")
                bookId = ids[0]
                authorId = ids[1]
                readlistId = ids[2]

                try:
                    sorgu = "INSERT INTO mediaread.user_has_readlist (user_idUser, readlist_idreadlist, book_idbook, book_author_id) VALUES ("+str(userId)+","+str(readlistId)+","+str(bookId)+","+str(authorId)+")"
                    db.cursor.execute(sorgu)
                    db.con.commit()

                    flash("You added this book in your readlist","success")

                except mysql.connector.Error:
                    flash("You already have this book in your readlist","danger")


            return redirect(url_for("readlist_page",user_id=userId,readlist_id=readlistId))



@app.route('/users/<int:user_id>/readBooks', methods = ["GET","POST"])
def readbook_page(user_id):

    if request.method == "GET":

        sorgu = """ SELECT *,DATE(mediaread.user_read_book.time)
                FROM mediaread.user
                LEFT JOIN mediaread.user_read_book
                ON mediaread.user.idUser = mediaread.user_read_book.user_id
                LEFT JOIN mediaread.book
                ON mediaread.book.idbook = mediaread.user_read_book.book_id
                LEFT JOIN mediaread.author
                ON mediaread.author.idAuthor = mediaread.user_read_book.author_id
                WHERE mediaread.user.idUser = """

        sorgu += str(user_id)
        sorgu += " ORDER BY mediaread.user_read_book.time"
        db.cursor.execute(sorgu)
        books = db.cursor.fetchall()
        length = len(books)
        empty = 0
        if books[0][6] is None:
            empty = 1

        sorgu = """
                SELECT *
                FROM mediaread.user_has_readlist
                LEFT JOIN mediaread.readlist
                ON mediaread.user_has_readlist.readlist_idreadlist = mediaread.readlist.idreadlist
                WHERE mediaread.user_has_readlist.user_idUser =
            """
        db.cursor.execute(sorgu+str(user_id)+" GROUP BY mediaread.user_has_readlist.readlist_idreadlist")
        readlists = db.cursor.fetchall()


        return render_template("readbook.html", books=books, length=length, empty=empty, readlists=readlists)

    else:

        ids = request.form.get("quoteVal")
        quote = request.form.get("quote")
        readlistId = request.form.getlist("readlist")
        if quote is not None:

            quote = quote.replace('"',"'")
            idler = ids.split("-")
            bookId = idler[0]
            authorId = idler[1]
            sorgu = "INSERT INTO mediaread.quote (quoteContent, user_id, book_id, author_id, time) VALUES (\""+quote+"\","+str(user_id)+","+str(bookId)+","+str(authorId)+", current_timestamp())"
            db.cursor.execute(sorgu)
            db.con.commit()


            return redirect(request.url)

        else:

            userId = session["userId"]
            for readId in readlistId:
                ids = readId.split("-")
                bookId = ids[0]
                authorId = ids[1]
                readlistId = ids[2]

                try:
                    sorgu = "INSERT INTO mediaread.user_has_readlist (user_idUser, readlist_idreadlist, book_idbook, book_author_id) VALUES ("+str(userId)+","+str(readlistId)+","+str(bookId)+","+str(authorId)+")"
                    db.cursor.execute(sorgu)
                    db.con.commit()
                    flash("You added this book in your readlist","success")

                except mysql.connector.Error:
                    flash("You already have this book in your readlist","danger")


            return redirect(url_for("readlist_page",user_id=userId,readlist_id=readlistId))



@app.route('/users/<int:user_id>', methods=["GET", "POST"])
def user(user_id):

    if request.method == "GET":
        sorgu = """
            SELECT *
            FROM mediaread.user
            LEFT JOIN mediaread.user_review_book
            ON mediaread.user.idUser = mediaread.user_review_book.user_id
            LEFT JOIN mediaread.book
            ON mediaread.book.idbook = mediaread.user_review_book.book_id
            LEFT JOIN mediaread.author
            ON mediaread.author.idAuthor = mediaread.user_review_book.author_id
            WHERE mediaread.user.idUser =
        """
        db.cursor.execute(sorgu+str(user_id)+" ORDER BY mediaread.user_review_book.time DESC")
        reviews = db.cursor.fetchall()
        length4 = 1
        if reviews[0][5] is None:
            length4 = 0

        sorgu = """
            SELECT *
            FROM mediaread.user
            LEFT JOIN mediaread.quote
            ON mediaread.user.idUser = mediaread.quote.user_id
            LEFT JOIN mediaread.book
            ON mediaread.book.idbook = mediaread.quote.book_id
            LEFT JOIN mediaread.author
            ON mediaread.author.idAuthor = mediaread.quote.author_id
            WHERE mediaread.user.idUser =
        """
        db.cursor.execute(sorgu+str(user_id)+" ORDER BY mediaread.quote.time DESC")
        quotes = db.cursor.fetchall()
        checkQ = 0
        if quotes[0][5] is None:
            checkQ = 1

        sorgu = """
            SELECT *
            FROM mediaread.user
            LEFT JOIN mediaread.user_has_book
            ON mediaread.user.idUser = mediaread.user_has_book.user_id
            LEFT JOIN mediaread.book
            ON mediaread.book.idbook = mediaread.user_has_book.book_id
            LEFT JOIN mediaread.author
            ON mediaread.author.idAuthor = mediaread.user_has_book.author_id
            WHERE mediaread.user.idUser =
        """
        db.cursor.execute(sorgu+str(user_id)+" ORDER BY mediaread.book.bookName ASC")
        books = db.cursor.fetchall()
        length6 = 1
        if books[0][5] is None:
            length6 = 0

        sorgu = """
            SELECT *
            FROM mediaread.user
            LEFT JOIN mediaread.user_read_book
            ON mediaread.user.idUser = mediaread.user_read_book.user_id
            LEFT JOIN mediaread.book
            ON mediaread.book.idbook = mediaread.user_read_book.book_id
            LEFT JOIN mediaread.author
            ON mediaread.author.idAuthor = mediaread.user_read_book.author_id
            WHERE mediaread.user.idUser =
        """
        db.cursor.execute(sorgu+str(user_id)+" ORDER BY mediaread.book.bookName ASC")
        read = db.cursor.fetchall()
        length5 = 1
        if read[0][5] is None:
            length5 = 0

        sorgu = """
            SELECT *
            FROM mediaread.user_has_readlist
            LEFT JOIN mediaread.readlist
            ON mediaread.user_has_readlist.readlist_idreadlist = mediaread.readlist.idreadlist
            WHERE mediaread.user_has_readlist.user_idUser = """ + str(user_id) + """ GROUP BY mediaread.user_has_readlist.readlist_idreadlist"""
        db.cursor.execute(sorgu)
        lists = db.cursor.fetchall()
        length3 = len(lists)
        check8 = False

        if "userId" in session:

            if session["userId"]:

                if session["userId"] != user_id:

                    sorgu = "SELECT * FROM mediaread.user_has_friend where userId = " + str(session["userId"]) + " and friendId = " + str(user_id)
                    db.cursor.execute(sorgu)
                    checkFriend = db.cursor.fetchone()

                    if checkFriend is not None:
                        check8 = True



        sorgu = """SELECT * FROM mediaread.user_has_friend
        LEFT JOIN mediaread.user
        ON mediaread.user_has_friend.friendId = mediaread.user.idUser
        where mediaread.user_has_friend.userId = """ + str(user_id)
        db.cursor.execute(sorgu)
        follow = db.cursor.fetchall()
        followLen = len(follow)

        sorgu = """SELECT * FROM mediaread.user_has_friend
        LEFT JOIN mediaread.user
        ON mediaread.user_has_friend.userId = mediaread.user.idUser
        where mediaread.user_has_friend.friendId = """ + str(user_id)
        db.cursor.execute(sorgu)
        follower = db.cursor.fetchall()
        followerLen = len(follower)


        return render_template("user.html", reviews=reviews, quotes=quotes, checkQ=checkQ, len3=len(quotes),
        books=books, len=len(books), read=read, len2=len(read), length3=length3, length4=length4,
        length5=length5, length6=length6, user_id=user_id, check8=check8, follower=follower, followerLen=followerLen,
        follow=follow, followLen=followLen)

    else:

        unfollow = request.form.get("unfollow")
        edited = request.form.get("editqoute")
        quoteid = request.form.get("quoteid")
        reviewid = request.form.get("reviewid")
        editreview = request.form.get("editreview")

        if unfollow is not None:

            sorgu = "DELETE FROM mediaread.user_has_friend WHERE userId = " + str(user_id) + " and friendId = " + str(unfollow)
            db.cursor.execute(sorgu)
            db.con.commit()


            return redirect(request.url)

        elif edited is not None:

            sorgu = "UPDATE mediaread.quote SET mediaread.quote.quoteContent = '" + str(edited) + "' WHERE mediaread.quote.idQuote = " + str(quoteid)
            db.cursor.execute(sorgu)
            db.con.commit()

            return redirect(request.url)

        elif editreview is not None:

            sorgu = "UPDATE mediaread.user_review_book SET review = '" + str(editreview) + "' WHERE mediaread.user_review_book.reviewId = " + str(reviewid)

            db.cursor.execute(sorgu)
            db.con.commit()

            return redirect(request.url)

        else:

            follower = session["userId"]
            follows = user_id

            if(follower != follows):

                try:
                    sorgu = "INSERT INTO mediaread.user_has_friend (userId, friendId, time) VALUES (" + str(follower) + ", " + str(follows) + ", current_timestamp())"
                    db.cursor.execute(sorgu)
                    db.con.commit()
                    flash("You succesfully followed","success")

                except mysql.connector.Error:
                    flash("You already gave a review to this book","danger")


            return redirect(request.url)



@app.route('/users/<int:user_id>/statistics')
def statistics(user_id):

    sorgu = """
        SELECT *
        FROM mediaread.user
        LEFT JOIN mediaread.user_review_book
        ON mediaread.user.idUser = mediaread.user_review_book.user_id
        LEFT JOIN mediaread.book
        ON mediaread.user_review_book.book_id = mediaread.book.idbook
        LEFT JOIN mediaread.author
        ON mediaread.book.author_id = mediaread.author.idAuthor
        WHERE mediaread.user.idUser =
    """
    db.cursor.execute(sorgu+str(user_id)+" ORDER BY mediaread.user_review_book.rate DESC")
    ratedBooks = db.cursor.fetchall()
    check1 = 0
    if ratedBooks[0][6] is None:
        check1 = 1

    sorgu = """
        SELECT SUM(mediaread.book.pageNumber), COUNT(mediaread.user_read_book.book_id)
        FROM mediaread.user
        LEFT JOIN mediaread.user_read_book
        ON mediaread.user.idUser = mediaread.user_read_book.user_id
        LEFT JOIN mediaread.book
        ON mediaread.user_read_book.book_id = mediaread.book.idbook
        WHERE mediaread.user.idUser =
    """
    db.cursor.execute(sorgu+str(user_id))
    infos = db.cursor.fetchone()
    if infos[0] is None:
        sum1 = 0
        bookpage = 0

    else:
        sum1 = infos[0]
        sum1 = int(sum1)
        bookpage = infos[1]
        bookpage = int(bookpage)

    sorgu = """
        SELECT mediaread.category.idCategory, mediaread.category.categoryName, COUNT(mediaread.book_has_category.category_id)
        FROM mediaread.user_read_book
        LEFT JOIN mediaread.book_has_category
        ON mediaread.user_read_book.book_id = mediaread.book_has_category.book_id AND mediaread.user_read_book.user_id =
    """ + str(user_id) + """
         LEFT JOIN mediaread.category
        ON mediaread.book_has_category.category_id = mediaread.category.idCategory
        GROUP BY mediaread.book_has_category.category_id
    """

    db.cursor.execute(sorgu)
    categories = db.cursor.fetchall()
    length = len(categories)

    sorgu = """
        SELECT mediaread.author.fullName, mediaread.author.idAuthor, COUNT(mediaread.author.idAuthor)
        FROM mediaread.user_read_book
        LEFT JOIN mediaread.book
        ON mediaread.book.idbook = mediaread.user_read_book.book_id AND mediaread.user_read_book.user_id =
    """ + str(user_id) + """
		LEFT JOIN mediaread.author
        ON mediaread.book.author_id = mediaread.author.idAuthor
        GROUP BY mediaread.author.idAuthor
        ORDER BY COUNT(mediaread.author.idAuthor) DESC
    """
    db.cursor.execute(sorgu)
    authors = db.cursor.fetchall()

    sorgu = "SELECT COUNT(mediaread.user_read_book.user_id) FROM mediaread.user_read_book WHERE mediaread.user_read_book.time > DATE_SUB(NOW(),INTERVAL 1 Year) AND mediaread.user_read_book.user_id = "
    db.cursor.execute(sorgu+str(user_id))
    lastYear = db.cursor.fetchone()

    sorgu = "SELECT COUNT(*) FROM mediaread.user_review_book WHERE user_id = " + str(user_id)
    db.cursor.execute(sorgu)
    reviewCount = db.cursor.fetchone()

    sorgu = "SELECT COUNT(*) FROM mediaread.quote WHERE user_id = " + str(user_id)
    db.cursor.execute(sorgu)
    quoteCount = db.cursor.fetchone()



    return render_template("statistic.html",ratedBooks=ratedBooks,check1=check1, sum1=sum1, bookpage=bookpage, categories=categories, length=length, authors=authors, lastYear=lastYear[0],reviewNum=reviewCount[0], quoteNum=quoteCount[0])



@app.route('/users/<int:user_id>/readlists', methods = ["GET","POST"])
def readlists_page(user_id):

    if request.method == "GET":

        sorgu = """
        SELECT *
        FROM mediaread.user_has_readlist
        LEFT JOIN mediaread.readlist
        ON mediaread.user_has_readlist.readlist_idreadlist = mediaread.readlist.idreadlist
        WHERE mediaread.user_has_readlist.user_idUser = """ + str(user_id) + """ GROUP BY mediaread.user_has_readlist.readlist_idreadlist"""
        db.cursor.execute(sorgu)
        lists = db.cursor.fetchall()


        return render_template("readlists.html", lists=lists)

    else:

        id = request.form.get("readlistId")

        sorgu = "DELETE FROM mediaread.user_has_readlist WHERE mediaread.user_has_readlist.readlist_idreadlist = " + str(id)
        db.cursor.execute(sorgu)
        db.con.commit()

        sorgu = "DELETE FROM mediaread.readlist WHERE mediaread.readlist.idreadlist = " + str(id)
        db.cursor.execute(sorgu)
        db.con.commit()



        return redirect(request.url)



@app.route('/users/<int:user_id>/readlists/<int:readlist_id>', methods = ["GET","POST"])
def readlist_page(user_id, readlist_id):

    if request.method == "GET":

        sorgu = """
            SELECT *
            FROM mediaread.user_has_readlist
            LEFT JOIN mediaread.readlist
            ON mediaread.user_has_readlist.readlist_idreadlist = mediaread.readlist.idreadlist
            LEFT JOIN mediaread.book
            ON mediaread.user_has_readlist.book_idbook = mediaread.book.idbook
            LEFT JOIN mediaread.author
            ON mediaread.book.author_id = mediaread.author.idAuthor
            WHERE mediaread.user_has_readlist.user_idUser = """ + str(user_id) + " AND mediaread.user_has_readlist.readlist_idreadlist = " + str(readlist_id)

        db.cursor.execute(sorgu)
        books = db.cursor.fetchall()
        length = len(books)


        return render_template("readlist.html", books=books, length=length)

    else:

        bookId = request.form.get("bookId")

        sorgu = "DELETE FROM mediaread.user_has_readlist WHERE mediaread.user_has_readlist.user_idUser="+str(user_id)+" AND mediaread.user_has_readlist.readlist_idreadlist="+str(readlist_id)+" AND mediaread.user_has_readlist.book_idbook="+str(bookId)
        db.cursor.execute(sorgu)
        db.con.commit()


        return redirect(request.url)



@app.route('/users/<int:user_id>/createreadlist', methods = ["GET","POST"])
def create_readlist_page(user_id):

    if request.method == "GET":

        sorgu = "SELECT * FROM mediaread.book LEFT JOIN mediaread.author ON mediaread.book.author_id = mediaread.author.idAuthor"
        db.cursor.execute(sorgu)
        books = db.cursor.fetchall()


        return render_template("createReadlist.html", books=books)

    else:

        ids = request.form.getlist("book")
        name = request.form.get("name")
        summary = request.form.get("summary")

        sorgu = "INSERT INTO mediaread.readlist (readlistName, summary) VALUES (\"" + name + "\" , \"" + summary + "\")"
        db.cursor.execute(sorgu)
        db.con.commit()

        sorgu = "SELECT * FROM mediaread.readlist order by idreadlist DESC LIMIT 1"
        db.cursor.execute(sorgu)
        data = db.cursor.fetchone()
        readlist_id = data[0]

        for id in ids:
            arr = id.split("-")
            book_id = arr[0]
            author_id = arr[1]
            sorgu = "INSERT INTO mediaread.user_has_readlist (user_idUser, readlist_idreadlist, book_idbook, book_author_id) VALUES ("+str(user_id)+","+str(readlist_id)+","+book_id+","+author_id+")"
            db.cursor.execute(sorgu)
            db.con.commit()



        return redirect(url_for("readlists_page",user_id=user_id))



@app.route('/users/<int:user_id>/saved', methods = ["GET", "POST"])
def saved(user_id):

    if request.method == "GET":

        sorgu = """

            SELECT *
            FROM mediaread.user_saved_book
            LEFT JOIN mediaread.book
            ON mediaread.user_saved_book.book_id = mediaread.book.idbook
            LEFT JOIN mediaread.author
            ON mediaread.book.author_id = mediaread.author.idAuthor
            WHERE mediaread.user_saved_book.user_id =""" + str(user_id)

        db.cursor.execute(sorgu)
        books = db.cursor.fetchall()

        length = len(books)


        return render_template("saved.html", books=books, length=length)

    else:

        bookId = request.form.get("deletefromsaved")
        sorgu = "DELETE FROM mediaread.user_saved_book WHERE user_id = "+str(user_id)+" AND book_id = "+str(bookId)
        db.cursor.execute(sorgu)
        db.con.commit()


        return redirect(request.url)



@app.route('/trends')
def trends():

    sorgu = """
        select mediaread.user_read_book.book_id,  mediaread.user_read_book.author_id, count(mediaread.user_read_book.book_id),
        mediaread.book.bookName, mediaread.book.bookImage, mediaread.author.fullName
        from  mediaread.user_read_book
        LEFT JOIN mediaread.book
        ON mediaread.user_read_book.book_id = mediaread.book.idbook
        LEFT JOIN mediaread.author
        ON mediaread.book.author_id = mediaread.author.idAuthor
        where mediaread.user_read_book.time >= DATE_SUB(NOW(),INTERVAL 1 MONTH)
        group by mediaread.user_read_book.book_id
    """
    db.cursor.execute(sorgu)
    trendbooks = db.cursor.fetchall()

    sorgu = """
        select mediaread.user_read_book.author_id, count(mediaread.user_read_book.author_id),
        mediaread.author.fullName, mediaread.author.authorImage
        from  mediaread.user_read_book
        LEFT JOIN mediaread.book
        ON mediaread.user_read_book.book_id = mediaread.book.idbook
        LEFT JOIN mediaread.author
        ON mediaread.book.author_id = mediaread.author.idAuthor
        where mediaread.user_read_book.time >= DATE_SUB(NOW(),INTERVAL 1 MONTH)
        group by mediaread.user_read_book.author_id
    """
    db.cursor.execute(sorgu)
    trendauthors = db.cursor.fetchall()


    return render_template("trends.html", trendbooks=trendbooks, trendauthors=trendauthors)



@app.route('/register', methods = ["GET","POST"])
def register_page():

    if request.method == "GET":

        return render_template("register.html")

    else:
        fullname = request.form["fullname"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        password = sha256_crypt.hash(password)

        if fullname and email and username and password:

            try:
                sorgu = "insert into mediaread.user (username, fullName, email, password) values (\""+username+"\", \""+fullname+"\", \""+email+"\", \""+password+"\")"
                db.cursor.execute(sorgu)
                db.con.commit()
                flash("REGISTERED SUCCESSFULLY","success")

            except mysql.connector.Error:
                flash("This username or email has registered before","danger")


        return redirect(url_for("login_page"))



@app.route('/users/<int:user_id>/account', methods = ["GET","POST"])
def account(user_id):

    sorgu = "SELECT * FROM mediaread.user Where idUser ="+str(user_id)
    db.cursor.execute(sorgu)
    infos = db.cursor.fetchone()

    if request.method == "GET":

        if "logged_in" in session:
            if session["logged_in"]:
                if user_id == session["userId"]:
                    return render_template("account.html",infos=infos)

        return redirect(url_for("home_page"))

    else:

        name = request.form.get("name")
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        oldpassword = request.form.get("oldpassword")
        newpassword = request.form.get("newpassword")
        newpassword2 = request.form.get("newpassword2")

        if newpassword2 is None:

            if  sha256_crypt.verify(password, infos[4]):

                sorgu = "UPDATE user SET username='"+username+"',email='"+email+"',fullName='"+name+"' WHERE idUser=" + str(user_id)
                db.cursor.execute(sorgu)
                db.con.commit()
                flash("INFORMATIONS SUCCESFULLY UPDATED","success")

            else:
                flash("WRONG PASSWORD","danger")

        else:

            if newpassword2 == newpassword:
                if sha256_crypt.verify(oldpassword, infos[4]):
                    newpassword = sha256_crypt.hash(newpassword)
                    sorgu = "UPDATE user SET password='"+newpassword+"' WHERE idUser="+str(user_id)
                    db.cursor.execute(sorgu)
                    db.con.commit()
                    flash("INFORMATIONS SUCCESFULLY UPDATED","success")
                else:
                    flash("WRONG PASSWORD","danger")
            else:
                flash("PASSWORDS DON'T MATCH","danger")






        return redirect(request.url)




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

                if  sha256_crypt.verify(password, check[0]):
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
    session["username"] = False
    session["userId"] = False
    flash("LOGGED OUT SUCCESSFULLY","success")
    return redirect(url_for("home_page"))



if __name__ == '__main__':
    app.run(threaded=True, port=5000)
