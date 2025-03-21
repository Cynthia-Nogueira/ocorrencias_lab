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


def obter_dados():
    #Busca dados no banco e retorna como lista.
    conn = get_db_connection()  # Abre a conexão com o BD
    cursor = conn.cursor(dictionary=True)  # Criar cursor corretamente

    cursor.execute("SELECT * FROM ocorrencias")  # Ajuste para sua tabela real
    dados = cursor.fetchall()  # Obtém os resultados

    cursor.close()  # Fecha o cursor
    conn.close()  # Fecha a conexão

    return dados  # Retorna os dados do banco



def obter_user_logado(current_user_id):
    if not current_user_id:
        return None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """SELECT CONCAT(nome, ' ', apelido) AS nome_completo FROM utilizador WHERE id = %s;"""
        cursor.execute(query, (current_user_id,))
        user = cursor.fetchone()
        return user[0] if user else None
    finally:
        cursor.close()
        conn.close()

