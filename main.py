from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QHBoxLayout, QLabel, QFrame, QGridLayout,
                             QPushButton, QComboBox, QTextEdit, QSizePolicy,
                             QFileDialog)
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PIL import Image
from random import choice
import pyperclip
import sys
from data.design import sort_quotes_ui, author_ui, edit_quote_ui, quote_browser_ui, add_quote_ui


# noinspection PyUnresolvedReferences
class SortQuotes(QWidget, sort_quotes_ui.Ui_Form):
    trigger = pyqtSignal(str, bool)

    def __init__(self, parent):
        super(SortQuotes, self).__init__()
        self.trigger.connect(parent.sort_quotes_slot)
        self.submitPushButton.clicked.connect(self.get_data)
        self.setupUi(self)

    def get_data(self):
        sort_method = next((b.text() for b in self.buttonGroup.buttons() if b.isChecked()), None)
        reverse = self.reverseCheckBox.isChecked()
        self.trigger.emit(sort_method, reverse)
        self.close()


class AuthorWindow(QWidget, author_ui.Ui_Form):
    def __init__(self, con, author):
        super(AuthorWindow, self).__init__()
        self.setupUi(self)
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


# noinspection PyUnresolvedReferences
class EditQuoteWindow(QWidget, edit_quote_ui.Ui_Form):
    quoteTextEdit: QTextEdit
    trigger = pyqtSignal()

    def __init__(self, con, quote, parent):
        super(EditQuoteWindow, self).__init__()
        self.setupUi(self)
        self.con = con
        self.quote = quote
        self.trigger.connect(parent.update_quotes_slot)
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
        self.trigger.emit()


# noinspection PyUnresolvedReferences
class AddQuoteWindow(QWidget, add_quote_ui.Ui_Form):
    trigger = pyqtSignal()

    def __init__(self, con, parent):
        super(AddQuoteWindow, self).__init__()
        self.setupUi(self)
        self.con = con
        self.image_filepath = ''
        self.trigger.connect(parent.update_quotes_slot)
        self.initUI()

    def initUI(self):
        self.isAuthorCheckbox.toggled.connect(self.disable_author_edit)
        self.chooseAuthorComboBox.currentIndexChanged.connect(self.disable_author_edit)
        self.quoteAddButton.clicked.connect(self.add_quote_to_db)
        self.quoteAddButton.setDisabled(True)
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
        INSERT INTO quotes (text, author_id, user_added)
        VALUES ("{data['quote']}", (SELECT id FROM authors WHERE name == "{data['name']}"), {int(True)})
        """)
        self.con.close()
        self.trigger.emit()
        self.close()


class QuoteBrowser(QMainWindow, quote_browser_ui.Ui_MainWindow):
    author_window: AuthorWindow
    quote_editter: EditQuoteWindow
    quote_adder: AddQuoteWindow
    quote_sort: SortQuotes

    def __init__(self):
        super(QuoteBrowser, self).__init__()
        self.setupUi(self)
        self.con = QSqlDatabase.addDatabase("QSQLITE")
        self.con.setDatabaseName('data/db/quotes_db.sqlite')
        self.sort = 'authors.name'
        self.reverse = False
        self.initUi()

    def initUi(self):
        self.logoLabel.setPixmap(QPixmap("data/img/logo.png"))
        self.bookmarksButton.clicked.connect(self.change_page)
        self.libraryButton.clicked.connect(self.change_page)
        self.myQuotesButton.clicked.connect(self.change_page)
        self.addQuoteButton.clicked.connect(self.add_quote)
        self.refreshPushButton.clicked.connect(self.update_quotes)
        self.sortPushButton.clicked.connect(self.open_sort_window)
        self.randomQuotePushButton.clicked.connect(self.random_quote)
        self.randomQuotePushButton.clicked.connect(self.change_page)
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
        elif text == 'Random Quote':
            self.stackedWidget.setCurrentIndex(3)

    def create_quote(self, quote) -> QFrame:
        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Panel)
        main_frame_layout = QGridLayout()
        main_frame.setLayout(main_frame_layout)

        author_frame = QFrame()
        author_layout = QHBoxLayout()
        author_button = QPushButton(f"Author: {quote['name']}")
        # author_button.setFlat(True)
        author_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        author_button.clicked.connect(self.show_author)
        author_layout.addWidget(author_button)
        author_layout.addWidget(QLabel(f"Birthday: {quote['birthday']}"))
        author_frame.setLayout(author_layout)

        quote_frame = QFrame()
        quote_frame.setStyleSheet("QLabel {background-color: white; font-style: italic;}")
        quote_layout = QVBoxLayout()
        text = QLabel(f"{quote['text']}")
        quote_layout.addWidget(text)
        quote_frame.setLayout(quote_layout)

        button_frame = QFrame()
        button_layout = QHBoxLayout()
        if quote['user_added']:
            quote_button_delete = QPushButton('Delete quote')
            quote_button_delete.clicked.connect(self.delete_quote)
            quote_button_edit = QPushButton('Edit quote')
            quote_button_edit.clicked.connect(self.edit_quote)
            button_layout.addWidget(quote_button_delete)
            button_layout.addWidget(quote_button_edit)
        if quote['name'] != 'You':
            quote_button_bookmark = QPushButton(
                'Add to bookmarks' if not quote['bookmarked'] else 'Remove from bookmarks')
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
        SET bookmarked = {int(flag)}
        WHERE text == "{label.text()}"
        """)
        self.con.close()
        self.update_quotes()

    def add_quote(self):
        self.quote_adder = AddQuoteWindow(self.con, self)
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
        self.quote_editter = EditQuoteWindow(self.con, label.text(), self)
        self.quote_editter.show()

    def copy_quote(self):
        label = self.get_label_from_quote_block(self.sender())
        pyperclip.copy(label.text())

    def update_quotes(self):
        data = self.get_data_from_db()
        self.clear_quote_layouts([self.libraryQuotesLayout, self.bookmarksQuotesLayout, self.myQuotesLayout])
        for quote in data:
            self.libraryQuotesLayout.addWidget(self.create_quote(quote))
            if quote['bookmarked']:
                self.bookmarksQuotesLayout.addWidget(self.create_quote(quote))
            if quote['name'] == 'You':
                self.myQuotesLayout.addWidget(self.create_quote(quote))

    def random_quote(self):
        self.clear_quote_layouts([self.randomQuoteLayout])
        random_quote = choice(self.get_data_from_db())
        self.randomQuoteLayout.addWidget(self.create_quote(random_quote))

    @staticmethod
    def clear_quote_layouts(layouts):
        for layout in layouts:
            for i in reversed(range(layout.count())):
                layout.itemAt(i).widget().setParent(None)

    def get_data_from_db(self):
        self.con.open()
        quote_columns = ['quotes.text', 'quotes.bookmarked', 'quotes.user_added',
                         'authors.name', 'authors.image_path', 'authors.birthday']
        query = QSqlQuery(f"""
        SELECT {', '.join(quote_columns)} 
        FROM quotes
        INNER JOIN authors ON quotes.author_id = authors.id       
        ORDER BY {self.sort} {'DESC' if self.reverse else 'ASC'}
""")
        data = []
        while query.next():
            data.append({key.split('.')[-1]: query.value(key) for key in quote_columns})
        return data

    def get_bookmarks_from_db(self):
        self.con.open()
        bookmark_columns = ['id', 'text', 'author_id']
        query = QSqlQuery()
        query.exec(f'SELECT {", ".join(bookmark_columns)} FROM quotes WHERE bookmarked = 1')
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

    @pyqtSlot(str, bool)
    def sort_quotes_slot(self, sort_method, reverse):
        if 'user' in sort_method:
            sort = 'quotes.user_added'
        elif 'quote' in sort_method:
            sort = 'quotes.text'
        else:   # default method of sorting
            sort = 'authors.name'
        self.sort = sort
        self.reverse = reverse
        self.update_quotes()

    @pyqtSlot()
    def update_quotes_slot(self):
        self.update_quotes()

    def open_sort_window(self):
        self.quote_sort = SortQuotes(self)
        self.quote_sort.show()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    qb = QuoteBrowser()
    qb.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
