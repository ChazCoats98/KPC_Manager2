import sys
import sqlite3
import hashlib
import re
import datetime
import time
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QWidget, QLineEdit, QLabel, QTableWidget, QTableWidgetItem, QDockWidget, QHeaderView
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QTableView,
    QTreeView,
    QTreeWidgetItem,
)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(213, 327)
        Form.setWindowTitle("Form")
        self.treeWidget = QtWidgets.QTreeWidget(Form)
        self.treeWidget.setGeometry(QtCore.QRect(0, 10, 211, 311))
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "Categories")
        self.treeWidget.setSortingEnabled(False)
        self.printtree()
        QtCore.QMetaObject.connectSlotsByName(Form)

    def printtree(self):
        self.treeWidget.setColumnCount(1)
        treeItem = QtWidgets.QTreeWidgetItem([])
        self.treeWidget.addTopLevelItem(treeItem)


        def displaytree():
            conn = sqlite3.connect('kpcmanager.db') # Connection to the Database 
            cursor = conn.cursor()
            table = cursor.execute(f"SELECT NAME FROM Test")
            for item in table.fetchall():
                name = str(item[0])
                branch_list = QtWidgets.QTreeWidgetItem([name])
                treeItem.addChild(branch_list)
                # I guess here should be a if statement.
                branch_list.addChild(QtWidgets.QTreeWidgetItem(["name"]))
        
        displaytree()

class dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KPC Manager")
        self.resize(1200, 800)
        
        layout = QVBoxLayout()
        layout.addWidget(Ui_Form)
        
app = QApplication(sys.argv)
window = dashboard()
window.show()
app.exec_()