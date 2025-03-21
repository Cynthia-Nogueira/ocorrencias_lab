from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection

# ------------------------------------- SELECT RESPONSAVEL ----------------------------------------

def get_responsavel():
    """ Obtém a lista de responsáveis do banco de dados """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT CONCAT(nome, ' ', apelido) AS nome_completo FROM utilizador;")
    responsaveis = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return responsaveis

# ------------------------------------------- OBTEM TODOSO OS USERS -------------------------------------------

def obter_lista_user():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """SELECT DISTINCT CONCAT (nome, ' ', apelido) as nome_completo, id FROM utilizador"""
    cursor.execute(query)
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

