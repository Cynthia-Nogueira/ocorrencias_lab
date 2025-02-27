from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mysql.connector
from nicegui import app, ui
import secrets
import smtplib
from token_helper import gerar_token, verificar_token, hash_senha



#-----------------------------------conecxao ao banco de dados -------------------------------------

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3305,
        user="admin",
        password="root",
        database="ocorrencias_lab"
    )

#---------------------------------------------- Gerador de tokens -----------------------------------------------

def gerar_token():
    return secrets.token_urlsafe(32)

def verificar_token(token):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM tokens WHERE token = %s AND created_at >= NOW() - INTERVAL 5 MINUTE", (token,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None


# ------------------------------- Limpa os tokens expirados do banco de dados -------------------------------

def limpar_tokens_expirados():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tokens WHERE created_at < NOW() - INTERVAL 1 WEEK")
    conn.commit()
    cursor.close()
    conn.close()


# ---------------------------- E-mail com Token ---------------------------
"""
# mensagem do email do token
def enviar_email(destinatario, token, assunto, corpo):
    remetente = "cynthia_nnogueira@hotmail.co"

    assunto = "Token para redefinição de senha"
    corpo = (f"Olá,\n\nAqui está o seu token para redefinir a senha: {token}\n\n"
             f"Esse token expira em 5 minutos."
             f"\n\nAtenciosamente,\nEquipe de Suporte")

    mensagem = MIMEMultipart()
    mensagem['From'] = remetente
    mensagem['To'] = destinatario
    mensagem['Subject'] = assunto

    try:
        # conexao com o servidor SMTP local (sem autenticação)
        with smtplib.SMTP('webmail.iep.pt', 25) as servidor:
            servidor.sendmail(remetente, destinatario, mensagem.as_string())
            print("E-mail enviado com sucesso!")
    except Exception as erro:
        print(f"Erro ao enviar o e-mail: {erro}")
        raise Exception("Erro ao tentar enviar o e-mail.")

"""

# ------------------------------- Pagina para inserir token ----------------------------

# Página para verificação de token (interface gráfica)

@ui.page('/verificar_token')
def verificar_token_page():
    app.add_static_files('/static', '../static')
    ui.add_head_html('<link rel="stylesheet" type="text/css" href="/static/styles.css">')

    with ui.card().classes("absolute-center items-center").style("background-color: #d2e9dd;"):
        ui.label("Verifique o token").classes("text-h4 text-center")

        token = ui.input("Insira o token recebido").classes("w-full")

        def validar_token():
            if not token.value:
                ui.notify("Preencha o campo com o token!", type="negative")
                return

            if verificar_token(token.value):
                ui.notify("Token verificado com sucesso!", type="positive")
                ui.navigate.to(f"/redefinir_senha/{token.value}")
            else:
                ui.notify("Token inválido ou expirado!", type="negative")

        ui.button("Verificar Token", on_click=validar_token, color="#008B8B").classes("w-full").style(
            "color: white; font-weight: bold")
        ui.button("Voltar", on_click=lambda: ui.navigate.to("/recuperacao_senha"), color="#008B8B").classes(
            "w-full").style(
            "color: white; font-weight: bold")


#---------------------------------- Redefinir a nova senha ----------------------------------


# Redefine a senha apos a validacao do token
def redefinir_senha_no_banco(token: str, nova_senha: str):
    if not verificar_token(token):
        raise ValueError("Token inválido ou expirado!")

    conn = get_db_connection()
    cursor = conn.cursor()
    senha_hash = hash_senha(nova_senha)

    try:
        # atualiza a senha no sql
        cursor.execute(
            "UPDATE utilizador SET password = %s WHERE username = (SELECT username FROM tokens WHERE token = %s)",
            (senha_hash, token)
        )

        # invalida o token da tabela
        cursor.execute("DELETE FROM tokens WHERE token = %s", (token,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()