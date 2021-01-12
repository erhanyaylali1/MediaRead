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

@app.route("/")
def index():
    return "Hello"


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
