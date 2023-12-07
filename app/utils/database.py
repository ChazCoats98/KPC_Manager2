import sqlite3

connection = sqlite3.connect('kpcmanager.db')
def showDb():
    print('connecting to database')
    
    cursor = connection.cursor()

    res = cursor.execute('''SELECT * FROM parts''')
    for row in res:
        print(row)
        
    addPart()

def addPart():
    cursor = connection.cursor()
    while 1:
        print('---------- Parts ----------')
        print('1. Add Part')
        print('2. Update Part')
        print('3. Exit')
        ch = int(input('Enter selection: '))
        
        if ch == 1:
            addPart = input('Enter Part Number: ')
            connection.execute('''INSERT INTO parts (pn) VALUES (?)''', [addPart])
            res = cursor.execute('''SELECT * FROM parts''')
            for row in res:
                print(row)
        elif ch == 3:
            connection.commit()
            connection.close()
            break
        