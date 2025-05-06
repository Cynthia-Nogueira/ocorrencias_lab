import secrets
import mysql.connector

# ------------------------------------------  token_helper.py --------------------------------------------------

def gerar_token():
    return secrets.token_urlsafe(32)


def verificar_token(token):
    conn = mysql.connector.connect(
        host="127.0.0.1",
        port=3305,
        user="admin",
        password="root",
        database="ocorrencias_lab"
    )
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username FROM tokens WHERE token = %s AND created_at >= NOW() - INTERVAL 5 MINUTE", (token,)
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None  # Retorna True se o token for válido; False caso contrário


# ------------------------------------------- encriptacao da senha -----------------------------------------------

# hash_utils.py
import bcrypt


# Função para criar hash da senha
def hash_senha(senha):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(senha.encode(), salt)
