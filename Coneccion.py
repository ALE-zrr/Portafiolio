import mysql.connector

def connection():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="formulario"
    )
    if mydb:
        print("Conexión exitosa a la base de datos")
        return mydb
    else:
        print("Error al conectar a la base de datos")
        return None