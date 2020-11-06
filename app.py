from flask import Flask, render_template, session
import views
from flask_mysqldb import MySQL

def create_app():

    app = Flask(__name__)
    app.secret_key = "MediaRead"
    
    app.config["MYSQL_HOST"] = "localhost"
    app.config["MYSQL_USER"] = "root"
    app.config["PASSWORD"] = "3347"
    app.config["MYSQL_DB"] = "mediaread"
    app.config["MYSQL_CURSORCLASS"] = "DictCursor"

    mysql = MySQL(app)

    app.add_url_rule("/", view_func=views.home_page)
    app.add_url_rule("/books", view_func=views.books_page)
    app.add_url_rule("/books/<int:book_id>", view_func=views.book_page)
    app.add_url_rule("/authors", view_func=views.authors_page)
    app.add_url_rule("/author/<int:author_id>", view_func=views.author_page)
    app.add_url_rule("/register", view_func=views.register_page, methods=["GET", "POST"])
    app.add_url_rule("/login", view_func=views.login_page, methods=["GET", "POST"])
    app.add_url_rule("/logout", view_func=views.logout_page)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
