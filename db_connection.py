import mysql.connector

config = {
    'user': 'root',
    'password': '',
    'host': '127.0.0.1',
    'database': 'parser_script_db',
    'raise_on_warnings': True
}

try:
    connection = mysql.connector.connect(**config)
except Exception as e:
    print(e)


