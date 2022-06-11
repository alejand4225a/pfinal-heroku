import mysql.connector as mysql

db = mysql.connect(
    host="academia.c1mebdhdxytu.us-east-1.rds.amazonaws.com",
    user="p7",
    password="ALrUBIaLYcHR",
    database="p7"
)
db.autocommit = True
