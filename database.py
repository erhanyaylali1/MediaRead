import MySQLdb
from flask_mysqldb import MySQL
import mysql.connector

class Database:

    def __init__(self, host, user, passwd, db):

        self.con = mysql.connector.connect(host=host, user=user, passwd=passwd, database=db)
        self.cursor = self.con.cursor()

    def toggle(self):

        if (self.check == 0):
            self.check = 1
        else:
            self.check = 0

