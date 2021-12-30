from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import os
import pathlib as pl
import sys
import sqlite3 as s3

from mainInterface import MainInterface
from addInteface import QDialogInteface

DATABASE = os.path.join(pl.Path(os.getcwd()).parent, os.path.join("DATA", "coffee.sqlite"))

with s3.connect(DATABASE) as con:
    dict_sorts = {so[0]: so[1] for so in con.cursor().execute("SELECT * FROM sorts")}
    reversed_sorts = {so[1]: so[0] for so in con.cursor().execute("SELECT * FROM sorts")}
    dict_categories = {ca[0]: ca[1] for ca in con.cursor().execute("SELECT * FROM categories")}
    rcategories = {ca[1]: ca[0] for ca in con.cursor().execute("SELECT * FROM categories")}


class ChangeDataBaseData(QDialog, QDialogInteface):
    def __init__(self, text, row_id=None, o=None, w=None, e=None, r=None, y=None, u=None):
        super().__init__()
        self.setupUi(self)
        self.button.clicked.connect(self.f)
        self.text, self.id = text, row_id

        if o is not None:
            o = reversed_sorts[o]
            w = rcategories[w]

        for widget, value in zip(
                (self.lineEdit, self.lineEdit_2, self.lineEdit_3, self.lineEdit_4, self.lineEdit_5, self.lineEdit_6),
                (o, e, w, r, y, u)):
            if value is not None:
                widget.setText(str(value))

    def f(self):
        sort = self.lineEdit.text()
        degree = self.lineEdit_2.text()
        category = self.lineEdit_3.text()
        taste = self.lineEdit_4.text()
        price = self.lineEdit_5.text()
        volume = self.lineEdit_6.text()

        if not all((sort, degree, category, taste, price, volume)):
            self.label_7.setText("Не указаны все критерии")
            return

        elif int(sort) not in range(1, 4):
            self.label_7.setText("Неверный сорт")
            return

        elif int(category) not in range(1, 3):
            self.label_7.setText("Не молотый/ в зернах")
            return

        else:
            self.label_7.setText('')

        if self.text == 'a':
            with s3.connect(DATABASE) as con:
                con.cursor().execute(f"INSERT INTO coffee(sort, shaped, fry_degree, taste, price, size)"
                                     f" VALUES('{sort}', '{category}', '{degree}', '{taste}', '{price}', '{volume}')")
            self.close()

        elif self.text == 'b':
            with s3.connect(DATABASE) as conn:
                conn.cursor().execute(
                    f"UPDATE coffee SET sort='{sort}', shaped = '{category}', fry_degree = '{degree}',"
                    f"taste = '{taste}', price = '{price}', size = '{volume}'"
                    f"WHERE ID = {self.id}")
            self.close()


class Window(MainInterface, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Another useless app to sort coffee')
        self.__coffee_func()
        self.append_new_coffee.clicked.connect(self.__append)
        self.swap_coffee_to_other.clicked.connect(self.__change)
        self.pushButton.clicked.connect(self.__coffee_func)

    def __coffee_func(self):
        """Решил для эксперимента сделать его приватным"""
        with s3.connect(DATABASE) as con:
            res = list(map(lambda x: [x[0], dict_sorts[x[1]], dict_categories[x[2]], *x[3:]],
                           con.cursor().execute("SELECT * FROM coffee").fetchall()))

        self.tableWidget.setColumnCount(7)
        self.tableWidget.setRowCount(len(res))

        self.tableWidget.setHorizontalHeaderLabels([
            "ID", "сорт", "молотый/в зернах", "степень обжарки", "вкус", "цена", "объем"])

        for i, row in enumerate(res):
            for j, cvalue in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(cvalue)))

    def __append(self):
        window = ChangeDataBaseData("a")
        window.exec()
        # # # # # # # # # #
        self.__coffee_func()

    def __change(self):
        if self.tableWidget.currentRow() == -1:
            return

        window = ChangeDataBaseData("b", *(self.tableWidget.item(self.tableWidget.currentRow(), i).text() for i in range(7)))

        window.exec()
        # # # # # # # # # #
        self.__coffee_func()


if __name__ == '__main__':
    q = QApplication(sys.argv)
    app = Window()
    app.show()
    sys.exit(q.exec())