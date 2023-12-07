import hashlib
import sqlite3

connection = sqlite3.connect('kpcmanager.db')
cursor = connection.cursor()

def login(email, pwd):
        
    auth = pwd.encode()
    password = hashlib.md5(auth).hexdigest()
    storedData = cursor.execute("SELECT * FROM user WHERE email = (?) AND password = (?)", [email, password])
    
    loginQueue = []
    
    for row in storedData:
        for x in row:
            loginQueue.append(x)
            
    if (email and password) in loginQueue:
        return True
    else:
        return False