from flask import Flask, render_template, current_app, abort, url_for, request, render_template, redirect, session, flash
from flask_mysqldb import MySQL
from database import Database
from MySQLdb import IntegrityError
import decimal


app = Flask(__name__)
app.secret_key = "MediaRead"
db = Database("127.0.0.1", 3307, "root", "3347", "mediaread")
db.check = 0


@app.route('/')
def home_page():

    userInfo = ""
    if session["username"] != "":

        db.cursor.execute("SELECT idUser, fullName from mediaread.user where username = \"" + str(session["username"]) + "\"")
        userInfo = db.cursor.fetchone()

    else:
        userInfo = ""
 
    return render_template("index.html", userInfo=userInfo)



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
        return render_template("books.html", allData=allData, length=length)    
    
    else:

        bookId = request.form.get("bookId")
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

        if quoteVal is None:
            reviewVal = reviewVal.split("-")
            user_id = reviewVal[0]
            author_id = reviewVal[1]
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


        else:
            quoteVal = quoteVal.split("-")
            user_id = quoteVal[0]
            author_id = quoteVal[1]
            sorgu = "INSERT INTO mediaread.quote (quoteContent, user_id, book_id, author_id, time) VALUES (\""+quote+"\","+str(user_id)+","+str(book_id)+","+str(author_id)+",current_timestamp())"

            db.cursor.execute(sorgu)
            db.con.commit()

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
        return render_template("library.html", datas=datas, length=length)

    else:

        bookId = request.form.get("bookId")
        rate = request.form.get("rate")
        review = request.form.get("review")
        idler = request.form.get("bookauthor_id")
        userId = user_id
        
        if bookId is not None:

            ids = bookId.split("-")
            bookId = ids[0]
            authorId = ids[1]
            sorgu = "DELETE FROM mediaread.user_has_book WHERE user_id = " + str(userId) + " AND book_id = " + str(bookId) + " AND author_id = " + str(authorId)
            
            db.cursor.execute(sorgu)
            db.con.commit()
            flash("You've delete this book in your library","success")

            return redirect(request.url)
        
        else:

            ids = idler.split("-")
            bookId = ids[0]
            authorId = ids[1]

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
            sorgu4 = "INSERT INTO mediaread.user_read_book (user_id, book_id, author_id, time) VALUES ("+str(userId)+", "+str(bookId)+", "+str(authorId)+",current_timestamp())"
            db.cursor.execute(sorgu4)
            db.con.commit()
            flash("You added this book to Read Books Page","success")
            return redirect(url_for("readbook_page",user_id=userId))
        


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
        print(sorgu)
        db.cursor.execute(sorgu)
        books = db.cursor.fetchall()
        length = len(books)
        empty = 0
        if books[0][6] is None:
            empty = 1
        return render_template("readbook.html", books=books, length=length, empty=empty)

    else:
        
        ids = request.form.get("quoteVal")
        quote = request.form.get("quote")
        idler = ids.split("-")
        bookId = idler[0]
        authorId = idler[1]

        sorgu = "INSERT INTO mediaread.quote (quoteContent, user_id, book_id, author_id, time) VALUES (\""+quote+"\","+str(user_id)+","+str(bookId)+","+str(authorId)+", current_timestamp())"
        db.cursor.execute(sorgu)
        db.con.commit()

        return redirect(request.url)



@app.route('/users/<int:user_id>')
def user(user_id):

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
    
    return render_template("user.html", reviews=reviews, quotes=quotes, len3=len(quotes), books=books, len=len(books), read=read, len2=len(read))



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

    return render_template("statistic.html",ratedBooks=ratedBooks,check1=check1, sum1=sum1, bookpage=bookpage, categories=categories, length=length, authors=authors, lastYear=lastYear[0])
    


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
