import hashlib
import sqlite3
import re
from PyQt5.QtWidgets import QMessageBox

connection = sqlite3.connect('kpcmanager.db')
cursor = connection.cursor()
emailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
passwordRegex = r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$'

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
        
def login(email, pwd):
        
    auth = pwd.encode()
    password = hashlib.md5(auth).hexdigest()
    storedData = cursor.execute("SELECT * FROM user WHERE email = (?) AND password = (?)", [email, password])
    
    loginQueue = []
    
    for row in storedData:
        for x in row:
            loginQueue.append(x)
            
    if (email and password) in loginQueue:
        renderDashboard()
    else:
        loginFailed()
        
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
    


