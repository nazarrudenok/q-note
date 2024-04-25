import sqlite3

conn = sqlite3.connect('main.db', check_same_thread=False)
cursor = conn.cursor()

# import pymysql

# HOST = 'localhost'
# USER = 'root'
# PASSWORD = ''
# DATABASE = 'q-note'

# conn = pymysql.connect(
#     host=HOST,
#     user=USER,
#     password=PASSWORD,
#     database=DATABASE
# )

# cursor = conn.cursor()