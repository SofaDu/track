import sqlite3

connection = sqlite3.connect('instance/orders.db')
cursor = connection.cursor()

# cursor.execute('insert into Users (tel_number, password, role) values (?, ?, ?), (?, ?, ?)',
#                ('111', '111', 1, '222', '222', 2))

cursor.execute('select * from Users')
users = cursor.fetchall()

for user in users:
    print(user)

connection.commit()
connection.close()
