import sqlite3

connection = sqlite3.connect('kpcmanager.db')

def createUser():
    cursor = connection.cursor()
    
    connection.execute('''CREATE TABLE user(
        email VARCHAR(255) NOT NULL,
        password VARCHAR(50) NOT NULL)''')
    
    connection.execute('''INSERT INTO user (email, password) VALUES ('ccoats@budney.com', 'MontegoBlueE92$')''')
    
    res = cursor.execute('''SELECT * from user''')
    
    for row in res:
        print(row)
        
    connection.commit()
    connection.close()
    
def addUser(email, password):
    cursor = connection.cursor()
    
    connection.execute('''INSERT INTO user (email, password) VALUES (?, ?)''', [email, password])
    
    res = cursor.execute('''SELECT email from user''')
    
    for row in res:
        print(row)
        
    connection.commit()
    connection.close()