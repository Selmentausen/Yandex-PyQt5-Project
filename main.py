from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget
from PyQt5 import uic
import pyperclip
import sqlite3
import sys


class QuoteBrowser(QMainWindow):
    QuoteList: QListWidget

    def __init__(self):
        super(QuoteBrowser, self).__init__()
        uic.loadUi('data/design.ui', self)
        self.show_quotes()

    def show_quotes(self):
        db = self.get_db_cursor()
        quotes = self.get_quotes_from_db()
        self.load_quotes_to_ListWidget()

    def load_quotes_to_ListWidget(self):
        pass

    def get_db(self):
        pass

    def get_quotes_from_db(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    qb = QuoteBrowser()
    qb.show()
    sys.exit(app.exec())
