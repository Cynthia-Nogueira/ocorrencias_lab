import bcrypt
import mysql.connector
from nicegui import app, ui

from Programa_NiceGui.paginas.token_helper import hash_senha
from db_conection import get_db_connection

from flask import session
import re

#--------------------------------------------- VERIFICA LOGIN ---------------------------------------------

# Função para verificar login
def check_login(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT  CONCAT(nome, ' ', apelido), password, id FROM utilizador WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    #print(result[0])

    if result and bcrypt.checkpw(password.encode(), result[1].encode()):
        app.storage.user["username"] = result[0]
        app.storage.user["userid"] = result[2]
        return True
    return False

ui.run(storage_secret="umsegredoqualquer")

#---------------------------------------- UNICIANDO SESSAO --------------------------------------------------

def realizar_login(username, password):
    user_id, type_user = check_login(username, password)
    if user_id:
        session['id_utilizador'] = user_id
        session['username'] = username
        session['type_user'] = type_user
        return True
    return False


#---------------------------------------- Cadastro Utilizador Page --------------------------------------------------

# Página de Cadastro de Usuário
def registro_page():
    app.add_static_files('/static', '../static')
    ui.add_head_html('<link rel="stylesheet" type="text/css" href="/static/styles.css">')

    with ui.card().classes("absolute-center mx-auto").style(
            "background-color: #d2e9dd; width: 500px; height: 615px; border-radius: 12px;"):
        ui.label("Criar Conta").classes("text-h4 text-center mx-auto")

        username = ui.input("Username", placeholder='Não deve conter acentos e espaços!').classes("w-full")
        nome = ui.input("Nome", placeholder='Ex: Maria').classes("w-full")
        apelido = ui.input("Apelido", placeholder='Ex: Almeida').classes("w-full")
        email = ui.input("E-mail", placeholder='Ex: joao.gomes@iep.pt').classes("w-full")
        password = ui.input("Senha", password=True, password_toggle_button=True).classes("w-full")
        confirm_password = ui.input("Confirmar Senha", password=True, password_toggle_button=True).classes("w-full")

        def try_registro():
            if not username.value or not email.value or not password.value or not confirm_password.value:
                ui.notify("Preencha todos os campos!", type="negative")
                return

            # impedi acentos no username
            if not re.match(r'^[a-zA-Z0-9_]+$', username.value):
                ui.notify("O username não deve conter acentos ou espaços!", type="negative")
                return


            # impedir acentos e força iniciais maiúsculas no nome e apelido
            nome_completo = f"{nome.value.strip()} {apelido.value.strip()}"


            if not re.match(r'^[A-Z][a-za-z]+ [A-Z][a-za-z]+$', nome_completo):
                ui.notify("O nome e apelido devem começar com letra maiúscula e não conter acentos!", type="negative")
                return

            if len(password.value) < 8 or not re.search(r'[A-Z]', password.value) or not re.search(r'\d',
                                                                                                   password.value):
                ui.notify("A senha deve ter pelo menos 8 caracteres, incluir uma letra maiúscula e um número.",
                          type="negative")
                return

            if password.value != confirm_password.value:
                ui.notify("As senhas não coincidem!", type="negative")
                return

            if not re.match(r"[^@]+@[^@]+\.[^@]+", email.value):
                ui.notify("E-mail inválido!", type="negative")
                return

            conn = get_db_connection()
            cursor = conn.cursor()

            # Criando hash seguro da senha
            senha_hash = hash_senha(password.value)

            try:
                query = "INSERT INTO utilizador (username, nome, apelido, email, password) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (username.value, nome.value, apelido.value, email.value, senha_hash))
                conn.commit()
                ui.notify("✅ Cadastro realizado com sucesso!", type="positive")

                # limpar os campos
                username.value = ''
                nome.value = ''
                apelido.value = ''
                email.value = ''
                password.value = ''
                confirm_password.value = ''

            except mysql.connector.Error as e:
                print(f"Erro ao cadastrar: {e}")  # Adicionando print para debug

                ui.notify(f"❌ Erro ao cadastrar: {e}", type="negative")
            finally:
                cursor.close()
                conn.close()

        ui.button("Confirmar", on_click=try_registro, color="#008B8B").style("color: white; font-weight: bold;"
                                    " background-color: #008B8B !important;").classes("w-full")
        ui.button("Voltar", on_click=lambda: ui.navigate.to("/"), color="#008B8B").style("color: white; font-weight: bold;"
                                    " background-color: #008B8B !important;").classes("w-full")


#------------------------------------------------ Login Page -----------------------------------------------------

# Página de Login
def login_page():
    app.add_static_files('/static', '../static')
    ui.add_head_html('<link rel="stylesheet" type="text/css" href="/static/styles.css">')

    with ui.card().classes("absolute-center items-center mx-auto").style(
        "background-color: #d2e9dd; width: 300px; height: 350px; border-radius: 12px;"):
        ui.label("Login").classes("text-h4 text-center")

        username = ui.input("Username", placeholder='Ex: Maria ou maria').classes("w-full")
        password = ui.input("Senha", password=True, password_toggle_button=True).classes("w-full")

        def try_login():
            if not username.value or not password.value:
                ui.notify("Preencha todos os campos!", type="negative")
                return

            if check_login(username.value, password.value):
                ui.navigate.to("/main")
            else:
                ui.notify("Utilizador ou senha incorretos", type="negative")

        # faz com que a tecla enter logue na conta
        password.on("keydown.enter", try_login)

        ui.button("Entrar", on_click=try_login).style("color: white; font-weight: bold;"
                        " background-color: #008B8B !important;").classes("w-full").style(
                        "color: white; font-weight: bold")

        # Texto que direciona a pagina de cadastro
        ui.label("Não tem uma conta?").classes("text-center").on("click", lambda: ui.navigate.to("/registro")).style(
            "cursor: pointer; color: #008B8B; text-decoration: underline;")

        # Texto que direciona para a pagina de recuperar senha
        ui.label("Esqueceu a senha?").classes("text-center").on("click", lambda: ui.navigate.to("/recuperacao_senha")).style(
            "cursor: pointer; color: #008B8B; text-decoration: underline;")

