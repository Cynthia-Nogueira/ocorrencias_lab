import re
import bcrypt
import mysql.connector
from nicegui import app, ui

from Programa_NiceGui.paginas.token_helper import hash_senha
from Programa_NiceGui.paginas import interface_recuperar_senha

from Programa_NiceGui.paginas.interface_formulario import novo_formulario
from interface_principal import main_page

# ------------------------------------------ Funcoes para login ----------------------------------------------

# Função para conectar ao banco de dados
def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3305,
        user="admin",
        password="root",
        database="ocorrencias_lab"
    )

#--------------------------------------------- FUNCAO QUE VERIFICA LOGIN ---------------------------------------------

# Função para verificar login
def check_login(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM utilizador WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result and bcrypt.checkpw(password.encode(), result[0].encode()):
        return True
    return False

#---------------------------------------- Cadastro Utilizador Page --------------------------------------------------

# Página de Cadastro de Usuário
def registro_page():
    app.add_static_files('/static', '../static')
    ui.add_head_html('<link rel="stylesheet" type="text/css" href="/static/styles.css">')

    with ui.card().classes("absolute-center").style("background-color: #d2e9dd ;"):
        ui.label("Criar Conta").classes("text-h4 text-center")

        username = ui.input("Nome de usuário").classes("w-full")
        email = ui.input("E-mail").classes("w-full")
        password = ui.input("Senha", password=True, password_toggle_button=True).classes("w-full")
        confirm_password = ui.input("Confirmar Senha", password=True, password_toggle_button=True).classes("w-full")

        def try_registro():
            if not username.value or not email.value or not password.value or not confirm_password.value:
                ui.notify("Preencha todos os campos!", type="negative")
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
                query = "INSERT INTO utilizador (username, email, password) VALUES (%s, %s, %s)"
                cursor.execute(query, (username.value, email.value, senha_hash))
                conn.commit()
                ui.notify("✅ Cadastro realizado com sucesso!", type="positive")
                ui.navigate.to("/")
            except mysql.connector.Error as e:
                ui.notify(f"❌ Erro ao cadastrar: {e}", type="negative")
            finally:
                cursor.close()
                conn.close()

        ui.button("Confirmar", on_click=try_registro, color="#008B8B").classes("w-full").classes("w-full").style("color: white; font-weight: bold")
        ui.button("Voltar", on_click=lambda: ui.navigate.to("/"), color="#008B8B").classes("w-full").classes("w-full").style("color: white; font-weight: bold")


#------------------------------------------------ Login Page -----------------------------------------------------

# Página de Login
def login_page():
    app.add_static_files('/static', '../static')
    ui.add_head_html('<link rel="stylesheet" type="text/css" href="/static/styles.css">')

    with ui.card().classes("absolute-center items-center").style("background-color: #d2e9dd ;"):
        ui.label("Login").classes("text-h4 text-center")

        username = ui.input("Utilizador").classes("w-full")
        password = ui.input("Senha", password=True, password_toggle_button=True).classes("w-full")

        def try_login():
            if not username.value or not password.value:
                ui.notify("Preencha todos os campos!", type="negative")
                return

            if check_login(username.value, password.value):
                ui.navigate.to("/main")
            else:
                ui.notify("Utilizador ou senha incorretos", type="negative")

        ui.button("Entrar", on_click=try_login, color="#008B8B").classes("w-full").style(
            "color: white; font-weight: bold")

        # Texto que direciona a pagina de cadastro
        ui.label("Não tem uma conta?").classes("text-center").on("click", lambda: ui.navigate.to("/registro")).style(
            "cursor: pointer; color: #008B8B; text-decoration: underline;")

        # Texto que direciona para a pagina de recuperar senha
        ui.label("Esqueceu a senha?").classes("text-center").on("click", lambda: ui.navigate.to("/recuperacao_senha")).style(
            "cursor: pointer; color: #008B8B; text-decoration: underline;")


# ---------------------------------------- Configuracao das rotas -------------------------------------------


@ui.page("/")
def index():
    login_page()

@ui.page("/registro")
def registro():
    registro_page()

@ui.page("/formulario")
def formulario():
    novo_formulario()

@ui.page("/main")
def main():
    main_page()

@ui.page("/redefinir_senha_page")
def redefinir_senha():
    interface_recuperar_senha.redefinir_senha_page()

@ui.page("/recuperacao_senha")
def recuperacao_senha():
    interface_recuperar_senha.recuperar_senha_page()

# Executa o aplicativo
ui.run()