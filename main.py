from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QHBoxLayout, QLabel, QFrame, QGridLayout,
                             QPushButton, QComboBox, QLayout, QTextBrowser)
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5 import uic
import sys


class QuoteBrowser(QMainWindow):
    libraryQuotesLayout: QLayout
    bookmarksQuotesLayout: QLayout

    def __init__(self):
        super(QuoteBrowser, self).__init__()
        uic.loadUi('data/design.ui', self)
        self.con = QSqlDatabase.addDatabase("QSQLITE")
        self.con.setDatabaseName('data/db/quotes_db.sqlite')
        self.initUi()

    def initUi(self):
        self.bookmarksButton.clicked.connect(self.change_page)
        self.libraryButton.clicked.connect(self.change_page)
        self.myQuotesButton.clicked.connect(self.change_page)
        self.addQuoteButton.clicked.connect(self.add_quote)
        self.stackedWidget.currentChanged.connect(self.load_quotes)
        self.load_quotes()

    def change_page(self):
        text = self.sender().text()
        if text == 'Library':
            self.stackedWidget.setCurrentIndex(0)
        elif text == 'Bookmarks':
            self.stackedWidget.setCurrentIndex(1)
        elif text == 'My Quotes':
            self.stackedWidget.setCurrentIndex(2)

    def create_quote(self, quote, author) -> QFrame:
        main_frame = QFrame()
        main_frame_layout = QGridLayout()
        main_frame.setLayout(main_frame_layout)

        author_frame = QFrame()
        author_frame.setFrameShape(QFrame.Panel)
        author_layout = QHBoxLayout()
        author_layout.addWidget(QLabel(author['name']))
        author_layout.addWidget(QLabel(author['birthday']))
        author_frame.setLayout(author_layout)

        quote_frame = QFrame()
        quote_frame.setFrameShape(QFrame.Panel)
        quote_layout = QVBoxLayout()
        text = QLabel(quote['text'])
        quote_layout.addWidget(text)
        quote_frame.setLayout(quote_layout)

        # TODO if user is author add two button delete and edit
        button_frame = QFrame()
        button_layout = QHBoxLayout()
        quote_button_bookmark = QPushButton(
            'Add to bookmarks' if quote['bookmarked'] == 'False' else 'Remove from bookmarks')
        quote_button_bookmark.clicked.connect(self.add_quote_to_bookmarks)
        button_layout.addWidget(quote_button_bookmark)
        button_frame.setLayout(button_layout)

        main_frame.setFrameShape(QFrame.Box)
        main_frame_layout.addWidget(author_frame, 0, 0)
        main_frame_layout.addWidget(quote_frame, 1, 0, 3, 1)
        main_frame_layout.addWidget(button_frame, 4, 0)
        return main_frame

    def add_quote_to_bookmarks(self):
        # Get quote block GridLayout where quote Label is stored
        layout: QGridLayout = self.sender().parentWidget().parentWidget().findChild(QGridLayout)
        # Get quote Label from GridLayout
        label = layout.itemAtPosition(1, 0).widget().findChild(QLabel)
        flag = True if self.sender().text() == 'Add to bookmarks' else False
        self.con.open()
        print('hello', flag)
        QSqlQuery(f"""
        UPDATE quotes
        SET bookmarked = "{flag}"
        WHERE text == "{label.text()}"
        """)
        self.con.close()
        self.load_quotes()

    def load_quotes(self):
        quotes = self.get_quotes_from_db()
        authors = self.get_authors_from_db()

        for i in reversed(range(self.libraryQuotesLayout.count())):
            self.libraryQuotesLayout.itemAt(i).widget().setParent(None)
        for i in reversed(range(self.bookmarksQuotesLayout.count())):
            self.bookmarksQuotesLayout.itemAt(i).widget().setParent(None)

        for quote in quotes:
            quote_author = next((a for a in authors if a['id'] == quote['author_id']), None)
            self.libraryQuotesLayout.addWidget(self.create_quote(quote, quote_author))
            if quote['bookmarked'] == 'True':
                self.bookmarksQuotesLayout.addWidget(self.create_quote(quote, quote_author))

    def get_authors_from_db(self):
        self.con.open()
        query = QSqlQuery()
        author_columns = ['id', 'name', 'image_path', 'birthday']
        query.exec(f'SELECT {", ".join(author_columns)} FROM authors')
        authors = self.get_query_dict(query, author_columns)
        self.con.close()
        return authors

    def get_quotes_from_db(self):
        self.con.open()
        quote_columns = ['id', 'text', 'bookmarked', 'author_id']
        query = QSqlQuery()
        query.exec(f'SELECT {", ".join(quote_columns)} FROM quotes')
        quotes = self.get_query_dict(query, quote_columns)
        self.con.close()
        return quotes

    def get_bookmarks_from_db(self):
        self.con.open()
        bookmark_columns = ['id', 'text', 'author_id']
        query = QSqlQuery()
        query.exec(f'SELECT {", ".join(bookmark_columns)} FROM quotes WHERE bookmarked == "True"')
        bookmarks = self.get_query_dict(query, bookmark_columns)
        self.con.close()
        return bookmarks

    @staticmethod
    def get_query_dict(query, columns):
        elements = []
        while query.next():
            elements.append({key: query.value(key) for key in columns})
        return elements

    def add_quote(self):
        self.quote_adder = AddQuoteWindow(self.con)
        self.quote_adder.show()


class AddQuoteWindow(QWidget):
    chooseAuthorComboBox: QComboBox

    def __init__(self, con):
        super(AddQuoteWindow, self).__init__()
        uic.loadUi('data/add_quote.ui', self)
        self.con = con
        self.initUI()

    def initUI(self):
        self.isAuthorCheckbox.toggled.connect(self.disable_author_edit)
        self.chooseAuthorComboBox.currentIndexChanged.connect(self.disable_author_edit)
        self.quoteAddButton.clicked.connect(self.add_quote_to_db)
        self.con.open()
        query = QSqlQuery("SELECT name FROM authors")
        while query.next():
            if query.value('name') != 'You':
                self.chooseAuthorComboBox.addItem(query.value('name'))
        self.con.close()

    def disable_author_edit(self):
        if isinstance(self.sender(), QComboBox):
            flag = False if self.sender().currentText() == 'No Author' else True
        else:
            flag = self.isAuthorCheckbox.isChecked()
            self.chooseAuthorComboBox.setDisabled(flag)
        self.nameLineEdit.setDisabled(flag)
        self.birthdayDateEdit.setDisabled(flag)

    def get_data(self):
        data = {'quote': self.quoteTextEdit.toPlainText()}
        if self.isAuthorCheckbox.isChecked():
            data['name'] = 'You'
            data['birthday'] = ''
        elif self.chooseAuthorComboBox.currentText() != 'No Author':
            data['name'] = self.chooseAuthorComboBox.currentText()
            self.con.open()
            query = QSqlQuery(f'SELECT birthday FROM authors WHERE name == "{data["name"]}"')
            query.next()
            data['birthday'] = query.value('birthday')
            self.con.close()
        else:
            data['name'] = self.nameLineEdit.text()
            data['birthday'] = self.birthdayDateEdit.date().toString('yyyy-MM-dd')
            self.add_author_to_db(data['name'], data['birthday'])
        return data

    def add_author_to_db(self, name, birthday):
        self.con.open()
        QSqlQuery(f"""
               INSERT INTO authors (name, birthday)
               VALUES ("{name}", "{birthday}")""")
        self.con.close()

    def add_quote_to_db(self):
        data = self.get_data()
        self.con.open()
        QSqlQuery(f"""
        INSERT INTO quotes (text, author_id)
        VALUES ("{data['quote']}", (SELECT id FROM authors WHERE name == "{data['name']}"))
        """)
        self.con.close()
        self.close()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    qb = QuoteBrowser()
    qb.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
