from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QHBoxLayout, QLabel, QFrame, QGridLayout,
                             QPushButton, QComboBox, QTextEdit, QSizePolicy,
                             QFileDialog)
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
import pyperclip
import sys
from PIL import Image


class AuthorWindow(QWidget):
    def __init__(self, con, author):
        super(AuthorWindow, self).__init__()
        uic.loadUi('data/author.ui', self)
        self.con = con
        self.author = author
        self.initUi()

    def initUi(self):
        self.con.open()
        query = QSqlQuery("")
        query.exec(f'SELECT image_path, birthday FROM authors WHERE name == "{self.author}"')
        query.next()
        image_path = query.value('image_path')
        birthday = query.value('birthday')
        pixmap = QPixmap(image_path)
        self.imageLabel.setPixmap(pixmap)
        self.nameLabel.setText(self.author)
        self.birthdayLabel.setText(birthday)
        self.con.close()


class EditQuoteWindow(QWidget):
    quoteTextEdit: QTextEdit

    def __init__(self, con, quote):
        super(EditQuoteWindow, self).__init__()
        uic.loadUi('data/edit_quote.ui', self)
        self.con = con
        self.quote = quote
        self.initUi()

    def initUi(self):
        self.quoteTextEdit.setText(self.quote)
        self.submitPushButton.clicked.connect(self.edit_quote)

    def edit_quote(self):
        self.con.open()
        QSqlQuery(f"""
        UPDATE quotes
        SET text == "{self.quoteTextEdit.toPlainText()}"
        WHERE text == "{self.quote}"
""")
        self.con.close()
        self.close()


class AddQuoteWindow(QWidget):
    def __init__(self, con):
        super(AddQuoteWindow, self).__init__()
        uic.loadUi('data/add_quote.ui', self)
        self.con = con
        self.image_filepath = ''
        self.initUI()

    def initUI(self):
        self.isAuthorCheckbox.toggled.connect(self.disable_author_edit)
        self.chooseAuthorComboBox.currentIndexChanged.connect(self.disable_author_edit)
        self.quoteAddButton.clicked.connect(self.add_quote_to_db)
        self.imagePushButton.clicked.connect(self.get_image)
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
        self.imagePushButton.setDisabled(flag)

    def get_image(self):
        self.image_filepath = QFileDialog.getOpenFileName(self, 'Choose picture', '',
                                                          'Картинка (*.jpg);;Картинка (*.png)')[0]
        self.imageLabel.setPixmap(QPixmap(self.image_filepath))

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
        filename = self.image_filepath.split('/')[-1]
        Image.open(self.image_filepath).save(filename)
        QSqlQuery(f"""
               INSERT INTO authors (name, birthday, image_path)
               VALUES ("{name}", "{birthday}", "{filename}")""")
        self.con.close()

    def add_quote_to_db(self):
        data = self.get_data()
        self.con.open()
        QSqlQuery(f"""
        INSERT INTO quotes (text, author_id, bookmarked, user_added)
        VALUES ("{data['quote']}", (SELECT id FROM authors WHERE name == "{data['name']}"), "False", "True")
        """)
        self.con.close()
        self.close()


class QuoteBrowser(QMainWindow):
    quote_editter: EditQuoteWindow
    quote_adder: AddQuoteWindow

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
        self.refreshPushButton.clicked.connect(self.update_quotes)
        self.exitButton.clicked.connect(self.close)
        self.stackedWidget.currentChanged.connect(self.update_quotes)
        self.update_quotes()

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
        main_frame.setFrameShape(QFrame.Panel)
        main_frame_layout = QGridLayout()
        main_frame.setLayout(main_frame_layout)

        author_frame = QFrame()
        author_layout = QHBoxLayout()
        author_button = QPushButton(f"Author: {author['name']}")
        author_button.setFlat(True)
        author_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        author_button.clicked.connect(self.show_author)
        author_layout.addWidget(author_button)
        author_layout.addWidget(QLabel(f"Birthday: {author['birthday']}"))
        author_frame.setLayout(author_layout)

        quote_frame = QFrame()
        quote_frame.setStyleSheet("QLabel {background-color: white; font-style: italic;}")
        quote_layout = QVBoxLayout()
        text = QLabel(f"{quote['text']}")
        quote_layout.addWidget(text)
        quote_frame.setLayout(quote_layout)

        button_frame = QFrame()
        button_layout = QHBoxLayout()
        if quote['user_added'] == 'True':
            quote_button_delete = QPushButton('Delete quote')
            quote_button_delete.clicked.connect(self.delete_quote)
            quote_button_edit = QPushButton('Edit quote')
            quote_button_edit.clicked.connect(self.edit_quote)
            button_layout.addWidget(quote_button_delete)
            button_layout.addWidget(quote_button_edit)
        if author['name'] != 'You':
            quote_button_bookmark = QPushButton(
                'Add to bookmarks' if quote['bookmarked'] == 'False' else 'Remove from bookmarks')
            quote_button_bookmark.clicked.connect(self.add_quote_to_bookmarks)
            button_layout.addWidget(quote_button_bookmark)
        quote_button_copy = QPushButton('Copy to clipboard')
        quote_button_copy.clicked.connect(self.copy_quote)
        button_layout.addWidget(quote_button_copy)
        button_frame.setLayout(button_layout)

        main_frame.setFrameShape(QFrame.Box)
        main_frame_layout.addWidget(author_frame, 0, 0)
        main_frame_layout.addWidget(quote_frame, 1, 0, 3, 0)
        main_frame_layout.addWidget(button_frame, 4, 0)
        return main_frame

    def add_quote_to_bookmarks(self):
        label = self.get_label_from_quote_block(self.sender())
        flag = True if self.sender().text() == 'Add to bookmarks' else False
        self.con.open()
        QSqlQuery(f"""
        UPDATE quotes
        SET bookmarked = "{flag}"
        WHERE text == "{label.text()}"
        """)
        self.con.close()
        self.update_quotes()

    def add_quote(self):
        self.quote_adder = AddQuoteWindow(self.con)
        self.quote_adder.show()

    def delete_quote(self):
        label = self.get_label_from_quote_block(self.sender())
        self.con.open()
        QSqlQuery(f"""
        DELETE FROM quotes
        WHERE text == "{label.text()}"
        """)
        self.update_quotes()

    def edit_quote(self):
        label = self.get_label_from_quote_block(self.sender())
        self.quote_editter = EditQuoteWindow(self.con, label.text())
        self.quote_editter.show()

    def copy_quote(self):
        label = self.get_label_from_quote_block(self.sender())
        pyperclip.copy(label.text())

    def update_quotes(self):
        quotes = self.get_quotes_from_db()
        authors = self.get_authors_from_db()

        self.clear_quote_layouts()
        for quote in quotes:
            quote_author = next((a for a in authors if a['id'] == quote['author_id']), None)
            self.libraryQuotesLayout.addWidget(self.create_quote(quote, quote_author))
            if quote['bookmarked'] == 'True':
                self.bookmarksQuotesLayout.addWidget(self.create_quote(quote, quote_author))
            if quote_author['name'] == 'You':
                self.myQuotesLayout.addWidget(self.create_quote(quote, quote_author))

    def clear_quote_layouts(self):
        for layout in [self.libraryQuotesLayout, self.bookmarksQuotesLayout, self.myQuotesLayout]:
            for i in reversed(range(layout.count())):
                layout.itemAt(i).widget().setParent(None)

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
        quote_columns = ['id', 'text', 'bookmarked', 'author_id', 'user_added']
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

    def show_author(self):
        name = self.sender().text().split(':')[1].strip()
        self.author_window = AuthorWindow(self.con, name)
        self.author_window.show()

    @staticmethod
    def get_query_dict(query, columns):
        elements = []
        while query.next():
            elements.append({key: query.value(key) for key in columns})
        return elements

    @staticmethod
    def get_label_from_quote_block(button):
        # Get quote block GridLayout where quote Label is stored
        layout = button.sender().parentWidget().parentWidget().findChild(QGridLayout)
        # Get quote Label by position from GridLayout
        label = layout.itemAtPosition(1, 0).widget().findChild(QLabel)
        return label


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    qb = QuoteBrowser()
    qb.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
