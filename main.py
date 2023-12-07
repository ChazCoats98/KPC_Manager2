import sys
import sqlite3
import hashlib
import re
import datetime
import time
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QWidget, QLineEdit, QLabel, QTableWidget, QTableWidgetItem, QDockWidget, QHeaderView
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlRelation
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QTableView,
    QTreeView,
    QTreeWidget,
    QTreeWidgetItem,
)


connection = sqlite3.connect('kpcmanager.db')
cursor = connection.cursor()
emailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
passwordRegex = r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$'

class loginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KPC Manager")
        self.resize(400, 200)
        
        layout = QGridLayout()
        
        # Email form 
        emailLabel = QLabel('Email:')
        self.emailInput = QLineEdit()
        self.emailInput.setPlaceholderText('Enter Email')
        layout.addWidget(emailLabel, 0, 0)
        layout.addWidget(self.emailInput, 0, 1)
        
        # Password form
        passwordLabel = QLabel('Password:')
        self.passwordInput = QLineEdit()
        self.passwordInput.setPlaceholderText('Enter Password')
        layout.addWidget(passwordLabel, 1, 0)
        layout.addWidget(self.passwordInput, 1, 1)
        
        # Login Button
        loginButton = QPushButton('Login')
        loginButton.clicked.connect(self.loginSubmit)
        layout.addWidget(loginButton, 2, 0, 1, 2)
        
        registerButton = QPushButton('Register')
        registerButton.clicked.connect(self.registerSubmit)
        layout.addWidget(registerButton, 3, 0, 1, 2)
        
        self.setLayout(layout)
        
        # function to handle button submit
    def loginSubmit(self):
        email = self.emailInput.text()
        pwd = self.passwordInput.text()
            
        login(email, pwd)
        
    def registerSubmit(self):
        global r
        r = registerWindow()
        r.show()
        window.close()
        
class registerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KPC Manager")
        self.resize(400, 200)
        
        layout = QGridLayout()
        
        # Email form 
        emailLabel = QLabel('Email:')
        self.emailInput = QLineEdit()
        self.emailInput.setPlaceholderText('Enter Email')
        layout.addWidget(emailLabel, 0, 0)
        layout.addWidget(self.emailInput, 0, 1)
        
        # Password form
        passwordLabel = QLabel('Password:')
        self.passwordInput = QLineEdit()
        self.passwordInput.setPlaceholderText('Enter Password')
        layout.addWidget(passwordLabel, 1, 0)
        layout.addWidget(self.passwordInput, 1, 1)
        
        # Repeat Password form
        repeatPasswordLabel = QLabel('Repeat Password:')
        self.repeatPasswordInput = QLineEdit()
        self.repeatPasswordInput.setPlaceholderText('repeat Password')
        layout.addWidget(repeatPasswordLabel, 2, 0)
        layout.addWidget(self.repeatPasswordInput, 2, 1)
        
        # Register Button
        loginButton = QPushButton('Register')
        loginButton.clicked.connect(self.registerUser)
        layout.addWidget(loginButton, 3, 0, 1, 2)
        
        self.setLayout(layout)
        
        # function to handle button submit
    def registerUser(self):
        email = self.emailInput.text()
        pwd = self.passwordInput.text()
        confPwd = self.repeatPasswordInput.text()
            
        register(email, pwd, confPwd)
        
class dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KPC Manager")
        self.resize(1200, 800)
        
        layout = QVBoxLayout()
        widget = QWidget(self)
        
        self.mainModel = QSqlTableModel(self)
        self.mainModel.setTable('parts')
        self.mainModel.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.mainModel.setHeaderData(0, Qt.Horizontal, 'ID')
        self.mainModel.setHeaderData(1, Qt.Horizontal, 'Part Number')
        self.mainModel.setHeaderData(2, Qt.Horizontal, 'Revision Letter')
        self.mainModel.setHeaderData(3, Qt.Horizontal, 'Net-Inspect Upload Date')
        self.mainModel.setHeaderData(4, Qt.Horizontal, 'Notes')
        self.mainModel.setHeaderData(5, Qt.Horizontal, 'Number of Features')
        self.mainModel.select()
        
        commitPart = QPushButton('Add Part')
        deletePart = QPushButton('Delete Part')
        
        self.treeWidget = QTreeWidget()
        
        
        self.view = QTableView()
        self.view.setModel(self.mainModel)
        header = self.view.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        
        deletePart.clicked.connect(lambda: self.mainModel.removeRow(self.view.currentIndex().row()))
        commitPart.clicked.connect(self.addPart)
        layout.addWidget(self.view)
        layout.addWidget(commitPart)
        layout.addWidget(deletePart)
        
        widget.setLayout(layout)
        
        self.setCentralWidget(widget)
        
    def addPart(self):
        self.mainModel.insertRows(self.mainModel.rowCount(), 1)
    
class partForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Part")
        self.resize(400, 200)
        
        layout = QGridLayout()
        
        # Part number form 
        partLabel = QLabel('Part Number:')
        self.partInput = QLineEdit()
        self.partInput.setPlaceholderText('Enter part number')
        layout.addWidget(partLabel, 0, 0)
        layout.addWidget(self.partInput, 0, 1)
        
        # Part revision form
        revLabel = QLabel('Revision Letter:')
        self.revInput = QLineEdit()
        self.revInput.setPlaceholderText('Enter revision letter')
        layout.addWidget(revLabel, 1, 0)
        layout.addWidget(self.revInput, 1, 1)
        
        # upload date form
        udLabel = QLabel('Last Net-Inspect Upload Date:')
        self.udInput = QLineEdit()
        self.udInput.setPlaceholderText('Enter upload date')
        layout.addWidget(udLabel, 2, 0)
        layout.addWidget(self.udInput, 2, 1)
        
        # Notes form
        notesLabel = QLabel('Notes:')
        self.notesInput = QLineEdit()
        self.notesInput.setPlaceholderText('Enter notes')
        layout.addWidget(notesLabel, 3, 0)
        layout.addWidget(self.notesInput, 3, 1)
        
        # Submit button Button
        addPartButton = QPushButton('Add Part')
        addPartButton.clicked.connect(self.submitPart)
        layout.addWidget(addPartButton, 4, 0, 1, 2)
        
        self.setLayout(layout)
    
    
class FeatureTable(QTableView):
    def __init__(self):
        super().__init__()
        self.childModel = QSqlTableModel(self)
        self.childModel.setTable('features')
        self.childModel.setHeaderData(0, Qt.Horizontal, 'ID')
        self.childModel.setHeaderData(1, Qt.Horizontal, 'KPC Number')
        self.childModel.setHeaderData(2, Qt.Horizontal, 'KPC Designation')
        self.childModel.setHeaderData(3, Qt.Horizontal, 'Feature Number')
        self.childModel.setHeaderData(4, Qt.Horizontal, 'Engine')
        self.childModel.setHeaderData(0, Qt.Horizontal, 'Parent Part')
        
        self.view = QTableView()
        self.view.setModel(self.childModel)
    
def createConnection():
    con = QSqlDatabase.addDatabase("QSQLITE")
    con.setDatabaseName("kpcmanager.db")
    if not con.open():
        QMessageBox.critical(
            None,
            "QTableView Example - Error!",
            "Database Error: %s" % con.lastError().databaseText(),
        )
        return False
    return True
        
def renderDashboard():
    global d
    d = dashboard()
    d.show()
    window.close()
    
def login(email, pwd):
        renderDashboard()
    # auth = pwd.encode()
    # password = hashlib.md5(auth).hexdigest()
    # storedData = cursor.execute("SELECT * FROM user WHERE email = (?) AND password = (?)", [email, password])
    
    # loginQueue = []
    
    # for row in storedData:
    #     for x in row:
    #         loginQueue.append(x)
            
    # if (email and password) in loginQueue:
    #     renderDashboard()
    # else:
    #     loginFailed()
        
def register(email, pwd, confPwd):
    if confPwd != pwd:
        passMismatch()
    elif(re.fullmatch(emailRegex, email)) and(re.fullmatch(passwordRegex, pwd)):
        enc = confPwd.encode()
        password = hashlib.md5(enc).hexdigest()
        storedData = cursor.execute("SELECT * FROM user WHERE email = (?)", [email])
        
        loginQueue = []
        
        for row in storedData:
            for x in row:
                loginQueue.append(x)
    
        if email in loginQueue:
            userExists()
        else:
            cursor.execute('INSERT INTO user (email, password) VALUES (?, ?)', [email, password])
            print('user has been registered')
        
    else:
        invalid()

def loginFailed():
    dlg = QMessageBox()
    dlg.setWindowTitle('ERROR')
    dlg.setText('Login Failed')
    dlg.exec()
    
def userExists():
    dlg = QMessageBox()
    dlg.setWindowTitle('ERROR')
    dlg.setText('User Already Exists')
    dlg.exec()
    
def invalid():
    dlg = QMessageBox()
    dlg.setWindowTitle('ERROR')
    dlg.setText('Invalid Email or Password')
    dlg.exec()
    
def passMismatch():
    dlg = QMessageBox()
    dlg.setWindowTitle('ERROR')
    dlg.setText('Passwords do not match')
    dlg.exec()

app = QApplication(sys.argv)
if not createConnection():
    sys.exit(1)
window = loginWindow()
window.show()
app.exec_()