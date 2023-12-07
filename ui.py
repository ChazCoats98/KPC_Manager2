import sqlite3

connection = sqlite3.connect('kpcmanager.db')
cursor = connection.cursor()

cursor.execute('CREATE TABLE features (feature_id INTEGER PRIMARY KEY, kpcnum INT, designation VARCHAR(5), featurenum INT, engine VARCHAR(20), part_id INT, FOREIGN KEY (part_id) REFERENCES parts(id))')
cursor.execute('INSERT INTO features (kpcnum, designation, featurenum, engine, part_id) VALUES (84740, "KPC1", 1, "TF33", 1)')

connection.commit()
connection.close()