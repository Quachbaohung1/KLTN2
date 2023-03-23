from flask import Flask
from flask_mysqldb import MySQL
import MySQLdb
    # Kết nối tới database
conn = MySQLdb.connect(host='localhost', user='root', password='Bungmobanhbao0303', db='login')

    # Tạo đối tượng cursor
cursor = conn.cursor()

    # Thực hiện truy vấn để lấy tất cả các user
cursor.execute('SELECT * FROM accounts')
users = cursor.fetchall()

    # In danh sách các user
for user in users:
    print(user)
conn.close()