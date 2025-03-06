import mysql.connector

def get_db_connection():
    """Estabelece e retorna uma conexão com o banco de dados."""
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3305,
        user="admin",
        password="root",
        database="ocorrencias_lab"
    )