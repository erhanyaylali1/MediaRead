import MySQLdb

class Database:

    def __init__(self, host, port, user, passwd, db):

        self.con = MySQLdb.Connect(host=host, port=port, user=user, passwd=passwd, db=db, use_unicode=True, charset="utf8")
        self.cursor = self.con.cursor()
        #self.createTable()
        #self.addSomeAuthors()
        #self.addSomeBooks()
