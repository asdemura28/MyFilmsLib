import sys
import webbrowser
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidgetItem, QTableWidget, QVBoxLayout, QPushButton, \
    QHBoxLayout, QComboBox, QLineEdit, QStyledItemDelegate, QMessageBox, QTabWidget
from PyQt5 import QtCore

con = sqlite3.connect("Films.db")
cur = con.cursor()

result = "SELECT Films.id, Films.title, Films.year, genres.title, " \
         "Films.duration, rating.rate FROM Films, genres, rating WHERE" \
         " genres.id = Films.genre and rating.id = Films.rating"

title = cur.execute("PRAGMA table_info('Films')").fetchall()
title = list(zip(*title))[1]
rating = ['0', '1', '2', '3', '4', '5']

change_row = []


def true_value(value):
    if not value:
        value = '%%'
    return value


class ReadOnlyDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        return


class MyFilms(QWidget):
    def __init__(self):
        super().__init__()
        self.loadUI()
        self.loadTable(cur.execute(result))

    def loadUI(self):
        self.setWindowTitle("MyFilmsLib")
        self.setGeometry(0, 0, 900, 900)
        self.main_btns = QHBoxLayout()
        self.search_lines = QHBoxLayout()
        self.search_btn = QHBoxLayout()
        self.back_lay = QVBoxLayout()

        self.tab = QTabWidget()
        menu_widget = QWidget()
        use_btns = QHBoxLayout(menu_widget)
        sort_widget = QWidget()
        sort_btns = QHBoxLayout(sort_widget)
        search_widget = QWidget()
        search_lay = QVBoxLayout(search_widget)
        search_lay.addLayout(self.search_lines)
        search_lay.addLayout(self.search_btn)
        self.tab.addTab(menu_widget, "Меню")
        self.tab.addTab(sort_widget, "Сортировка")
        self.tab.addTab(search_widget, "Поиск")
        self.tab.setFixedHeight(150)

        self.sort_year = QPushButton("По году")
        self.sort_duration = QPushButton("По длительности")
        self.sort_rating = QPushButton("По рейтингу")
        self.name = QLineEdit()
        self.name.setPlaceholderText('Укажите название')
        self.year = QLineEdit()
        self.year.setPlaceholderText('Укажите год выпуска')
        self.duration = QLineEdit()
        self.duration.setPlaceholderText('Укажите продолжительность')
        self.genres = QComboBox()
        titles = cur.execute("select title from genres")
        self.genres.addItem("")
        for title in titles:
            self.genres.addItem(str(title)[2:-3])
        self.btn = QPushButton("Найти")
        self.add_btn = QPushButton("Добавить")
        self.change_btn = QPushButton("Изменить")
        self.del_btn = QPushButton("Удалить")
        self.info_btn = QPushButton("Подробнее")
        self.table = QTableWidget()

        self.main_btns.addWidget(self.tab)
        sort_btns.addWidget(self.sort_year)
        sort_btns.addWidget(self.sort_duration)
        sort_btns.addWidget(self.sort_rating)
        self.search_lines.addWidget(self.name)
        self.search_lines.addWidget(self.year)
        self.search_lines.addWidget(self.duration)
        self.search_lines.addWidget(self.genres)
        use_btns.addWidget(self.add_btn)
        use_btns.addWidget(self.change_btn)
        use_btns.addWidget(self.del_btn)
        use_btns.addWidget(self.info_btn)
        self.search_btn.addWidget(self.btn)

        self.back_lay.addLayout(self.main_btns)
        self.back_lay.addWidget(self.table)
        self.setLayout(self.back_lay)

        self.btn.clicked.connect(self.pushedBtn)
        self.add_btn.clicked.connect(self.addFilm)
        self.change_btn.clicked.connect(self.changeFilm)
        self.del_btn.clicked.connect(self.delFilm)
        self.info_btn.clicked.connect(self.infoFilm)
        self.sort_year.clicked.connect(self.sortFilms)
        self.sort_duration.clicked.connect(self.sortFilms)
        self.sort_rating.clicked.connect(self.sortFilms)

        self.sort_flags = [True, True, True]

    def sortFilms(self):
        if self.sender() == self.sort_year:
            if self.sort_flags[0]:
                key_sort = 'year desc'
            else:
                key_sort = 'year asc'
            self.sort_flags[0] = not self.sort_flags[0]
        elif self.sender() == self.sort_duration:
            if self.sort_flags[1]:
                key_sort = 'duration desc'
            else:
                key_sort = 'duration asc'
            self.sort_flags[1] = not self.sort_flags[1]
        else:
            if self.sort_flags[2]:
                key_sort = 'rating desc'
            else:
                key_sort = 'rating asc'
            self.sort_flags[2] = not self.sort_flags[2]
        result_all = cur.execute(f'select Films.id, Films.title, Films.year, genres.title, Films.duration,' \
                                 f' rating.rate from Films, genres, rating where genres.id = Films.genre and'
                                 f' rating.id = Films.rating order by {key_sort}')
        self.loadTable(result_all)

    def pushedBtn(self):
        cur_year = self.year.text()
        cur_duration = self.duration.text()
        cur_name = self.name.text()
        cur_genre = self.genres.currentText()
        cur_select = f"select Films.id, Films.title, Films.year," \
                     f" genres.title, Films.duration, rating.rate from genres," \
                     f" Films, rating where genres.id == Films.genre and genres.title like '{true_value(cur_genre)}'" \
                     f" and Films.title like '%{true_value(cur_name)}%' and Films.duration" \
                     f" like '{true_value(cur_duration)}' and Films.year like '{true_value(cur_year)}'" \
                     f" and rating.id = Films.rating"
        result_all = cur.execute(cur_select)
        self.loadTable(result_all)

    def infoFilm(self):
        global change_row
        change_row = []
        if self.table.currentRow() != -1:
            for i in range(len(title)):
                change_row.append(self.table.item(self.table.currentRow(), i).text())
            address = f'https://www.google.com/search?client=opera&q=' \
                      f'{change_row[1]} фильм&sourceid=opera&ie=UTF-8&oe=UTF-8'
            webbrowser.open_new_tab(address)
        else:
            message = "Выберите фильм"
            QMessageBox.question(self, 'Ошибка', message, QMessageBox.Ok)

    def changeFilm(self):
        global change_row
        change_row = []
        if self.table.currentRow() != -1:
            for i in range(len(title)):
                change_row.append(self.table.item(self.table.currentRow(), i).text())
            self.change_win = CreateChangeWin()
            self.change_win.show()
        else:
            message = "Выберите запись для изменения"
            QMessageBox.question(self, 'Ошибка', message, QMessageBox.Ok)

    def addFilm(self):
        self.add_win = CreateAddWin()
        self.add_win.show()

    def delFilm(self):
        if self.table.currentRow() != -1:
            message = "Удалить запись?"
            reply = QMessageBox.question(self, 'Подтверждение', message, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                cur.execute(f'delete from Films where id = "{int(self.table.item(self.table.currentRow(), 0).text())}"')
                con.commit()
                self.pushedBtn()
            else:
                pass
        else:
            message = "Выберите запись для удаления"
            QMessageBox.question(self, 'Ошибка', message, QMessageBox.Ok)

    def loadTable(self, result):
        self.table.setRowCount(0)
        self.table.setColumnCount(len(title))
        self.table.hideColumn(0)
        self.table.setHorizontalHeaderLabels(title)
        delegate = ReadOnlyDelegate(self)
        for row in range(self.table.columnCount()):
            self.table.setItemDelegateForColumn(row, delegate)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        self.table.resizeColumnsToContents()


class CreateAddWin(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setGeometry(0, 450, 900, 150)
        self.setWindowTitle("Добавление фильма")
        self.main_lay = QVBoxLayout()
        self.hor_lay = QHBoxLayout()
        self.ver_lay = QHBoxLayout()

        self.title = QLineEdit()
        self.title.setPlaceholderText("Введите название")
        self.year = QLineEdit()
        self.year.setPlaceholderText("Введите год")
        self.genre = QComboBox()
        titles = cur.execute("select title from genres")
        for title in titles:
            self.genre.addItem(str(title)[2:-3])
        self.duration = QLineEdit()
        self.duration.setPlaceholderText("Укажите длительность")
        self.rating = QComboBox()
        rating = cur.execute("select rate from rating")
        for rate in rating:
            self.rating.addItem(str(rate)[2:-3])
        self.add_btn = QPushButton("Добавить")
        self.cancel_btn = QPushButton("Отмена")

        self.hor_lay.addWidget(self.title)
        self.hor_lay.addWidget(self.year)
        self.hor_lay.addWidget(self.genre)
        self.hor_lay.addWidget(self.duration)
        self.hor_lay.addWidget(self.rating)
        self.ver_lay.addWidget(self.add_btn)
        self.ver_lay.addWidget(self.cancel_btn)
        self.main_lay.addLayout(self.hor_lay)
        self.main_lay.addLayout(self.ver_lay)
        self.setLayout(self.main_lay)

        self.cancel_btn.clicked.connect(self.cancelWin)
        self.add_btn.clicked.connect(self.addFilm)

    def cancelWin(self):
        self.close()

    def addFilm(self):
        if self.title.text() and self.year.text() and self.duration.text() and self.rating.currentText():
            cur_rating = \
            cur.execute(f'select id from rating where rate like "{self.rating.currentText()}"').fetchall()[0][0]
            cur_genre = \
            cur.execute(f'select id from genres where title like "{self.genre.currentText()}"').fetchall()[0][0]
            ins = f'insert into Films (title, year, genre, duration, rating)' \
                  f' values("{self.title.text()}", "{int(self.year.text())}", "{cur_genre}",' \
                  f' "{int(self.duration.text())}", "{cur_rating}")'
            cur.execute(ins)
            con.commit()
            ex.loadTable(cur.execute(result))
            self.close()
        else:
            message = "Заполните все поля"
            reply = QMessageBox.question(self, 'Ошибка', message, QMessageBox.Ok)


class CreateChangeWin(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setGeometry(0, 450, 900, 150)
        self.setWindowTitle("Изменение")
        self.main_lay = QVBoxLayout()
        self.hor_lay = QHBoxLayout()
        self.ver_lay = QHBoxLayout()

        self.title = QLineEdit()
        self.title.setText(change_row[1])
        self.year = QLineEdit()
        self.year.setText(change_row[2])
        self.genre = QComboBox()
        titles = cur.execute("select title from genres")
        for title in titles:
            self.genre.addItem(str(title)[2:-3])
        cur_index = cur.execute(f"select id from genres where title like '{change_row[3]}'").fetchall()[0][0] - 1
        self.genre.setCurrentIndex(cur_index)
        self.duration = QLineEdit()
        self.duration.setText(change_row[4])
        self.rating = QComboBox()
        rating = cur.execute("select rate from rating")
        for rate in rating:
            self.rating.addItem(str(rate)[2:-3])
        cur_index = cur.execute(f"select id from rating where rate like '{change_row[5]}'").fetchall()[0][0]
        print(cur_index)
        self.rating.setCurrentIndex(cur_index)
        self.change_btn = QPushButton("Изменить")
        self.cancel_btn = QPushButton("Отмена")

        self.hor_lay.addWidget(self.title)
        self.hor_lay.addWidget(self.year)
        self.hor_lay.addWidget(self.genre)
        self.hor_lay.addWidget(self.duration)
        self.hor_lay.addWidget(self.rating)
        self.ver_lay.addWidget(self.change_btn)
        self.ver_lay.addWidget(self.cancel_btn)
        self.main_lay.addLayout(self.hor_lay)
        self.main_lay.addLayout(self.ver_lay)
        self.setLayout(self.main_lay)

        self.cancel_btn.clicked.connect(self.cancelWin)
        self.change_btn.clicked.connect(self.changeFilm)

    def cancelWin(self):
        self.close()

    def changeFilm(self):
        cur_genre = cur.execute(f'select id from genres where title'
                                f' like "{self.genre.currentText()}"').fetchall()[0][0]
        cur_rating = cur.execute(f'select id from rating where rate'
                                 f' like "{self.rating.currentText()}"').fetchall()[0][0]
        change = f"update Films set title = '{self.title.text()}', year = '{self.year.text()}'," \
                 f" genre = '{cur_genre}', duration = '{self.duration.text()}'," \
                 f" rating = '{cur_rating}' where id = '{change_row[0]}'"
        cur.execute(change)
        con.commit()
        ex.loadTable(cur.execute(result))
        self.close()


app = QApplication(sys.argv)
ex = MyFilms()
ex.show()
sys.exit(app.exec_())
