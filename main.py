from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5 import uic
import pyperclip
import sqlite3
import sys


class QuoteBrowser(QMainWindow):
    QuoteList: QListWidget

    def __init__(self):
        super(QuoteBrowser, self).__init__()
        uic.loadUi('data/design.ui', self)
        self.con = QSqlDatabase.addDatabase("QSQLITE")
        self.con.setDatabaseName('data/quotes.sqlite')
        self.show_quotes()

    def show_quotes(self):
        quotes = self.get_quotes_from_db()
        self.load_quotes_to_application(quotes)

    def load_quotes_to_application(self, quotes):
        for quote in quotes:
            self.QuoteList.addItem(quote)

    def get_quotes_from_db(self):
        quotes = []
        self.con.open()
        query = QSqlQuery()
        query.exec('SELECT quote FROM quotes')
        while query.next():
            quotes.append(query.value(0))
        self.con.close()
        return quotes


if __name__ == '__main__':
    app = QApplication(sys.argv)
    qb = QuoteBrowser()
    qb.show()
    sys.exit(app.exec())
