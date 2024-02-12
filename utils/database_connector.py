import mysql.connector
from time import sleep

print("Waiting to connect...")
sleep(60)

db = mysql.connector.connect(user="root", password="root", host="db", database="IC_Moves")
cursor = db.cursor(dictionary=True)