import secrets
from token_helper import  hash_senha
from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection


#-------------------------------------------- redefinindo a senha -----------------------------------

# redefine a senha clicar no link
def redefinir_senha_no_banco(email: str, nova_senha: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    senha_hash = hash_senha(nova_senha)  # codifica a nova senha

    try:
        # verifica se o e-mail existe no banco antes de atualizar
        cursor.execute("SELECT username FROM utilizador WHERE email = %s", (email,))
        result = cursor.fetchone()

        if not result:
            raise ValueError("E-mail não encontrado!")

        # atualiza a senha no banco
        cursor.execute("UPDATE utilizador SET password = %s WHERE email = %s", (senha_hash, email))
        conn.commit()

        print("Nova senha definida com sucesso!")
    finally:
        cursor.close()
        conn.close()

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
"""
def limpar_tokens_expirados():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tokens WHERE created_at < NOW() - INTERVAL 1 WEEK")
    conn.commit()
    cursor.close()
    conn.close()

"""
# ------------------------------- Pagina para inserir token ----------------------------

"""
# Página para verificação de token (interface gráfica)
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

        ui.button("Verificar Token", on_click=validar_token).style("color: white; font-weight: bold;"
                                    " background-color: #008B8B !important;").classes("w-full")
        ui.button("Voltar", on_click=lambda: ui.navigate.to("/recuperacao_senha")).style("color: white; font-weight: bold;"
                                    " background-color: #008B8B !important;").classes("w-full")

"""
#---------------------------------- Redefinir a nova senha ----------------------------------

