import mysql.connector

database = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root123"
)

cursor_object = database.cursor()

cursor_object.execute("CREATE DATABASE crm")

print("All Done!")