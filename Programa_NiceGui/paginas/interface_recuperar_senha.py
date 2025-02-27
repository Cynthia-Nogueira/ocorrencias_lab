import re

from Programa_NiceGui.paginas.send_email import sendmail
from interface_token import gerar_token, redefinir_senha_no_banco
from send_email import sendmail
import mysql.connector
from nicegui import app, ui

import interface_login_cadastro

#-----------------------------------conecxao ao banco de dados -------------------------------------

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3305,
        user="admin",
        password="root",
        database="ocorrencias_lab"
    )

#------------------------------------------- Recuperar senha page -----------------------------------------------------

@ui.page('/recuperar_senha')
def recuperar_senha_page():
    app.add_static_files('/static', '../static')
    ui.add_head_html('<link rel="stylesheet" type="text/css" href="/static/styles.css">')

    with ui.card().classes("absolute-center items-center").style("background-color: #d2e9dd ;"):
        ui.label("Digite seu e-mail").classes("text-h4 text-center")

        email = ui.input("E-mail").classes("w-full")

        # verifica se o email foi preenchido
        def enviar_token():
            if not email.value:
                ui.notify("Preencha o campo com seu e-mail!", type="negative")
                return

            # valida o e-mail
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email.value):
                ui.notify("E-mail inválido!", type="negative")
                return

            conn = get_db_connection()
            cursor = conn.cursor()

            try:
                # Verifica se o e-mail existe no banco
                cursor.execute("SELECT username FROM utilizador WHERE email = %s", (email.value,))
                result = cursor.fetchone()

                if result:
                    username = result[0]
                    token = gerar_token()         # funcao que gera o token

                    # insere o token na tabela
                    cursor.execute("INSERT INTO tokens (username, token, created_at) VALUES (%s, %s, NOW())",
                                   (username, token))
                    conn.commit()

                    # envia o token para o e-mail
                    sendmail(email.value, token)

                    ui.notify(f"Token enviado para o e-mail {email.value}!", type="positive")
                else:
                    ui.notify("E-mail não encontrado!", type="negative")

            except Exception as e:
                ui.notify(f"Erro ao processar: {e}", type="negative")
            finally:
                cursor.close()
                conn.close()

        ui.button("Enviar Token", on_click=enviar_token, color="#008B8B").classes("w-full").style(
            "color: white; font-weight: bold")



# Redefinição de senha
@ui.page('/redefinir_senha')
def redefinir_senha_page(token: str):
    app.add_static_files('/static', '../static')
    ui.add_head_html('<link rel="stylesheet" type="text/css" href="/static/styles.css">')

    with ui.card().classes("absolute-center items-center").style("background-color: #d2e9dd ;"):
        ui.label("Redefinir Senha").classes("text-h4 text-center")

        # confirmacao nova senha
        new_password = ui.input("Nova Senha", password=True, password_toggle_button=True) \
            .classes("w-full").props(
            title="A senha deve ter pelo menos 8 caracteres, incluir uma letra maiúscula e um número.")
        confirm_new_password = ui.input("Confirmar Senha", password=True, password_toggle_button=True).classes("w-full")

        # redefinindo a senha
        def redefinir_senha():
            if not new_password.value or not confirm_new_password.value:
                ui.notify("Preencha todos os campos!", type="negative")
                return

            if new_password.value != confirm_new_password.value:
                ui.notify("As senhas não coincidem!", type="negative")
                return

            if len(new_password.value) < 8 or not re.search(r'[A-Z]', new_password.value) or not re.search(r'\d',
                                                                                                           new_password.value):
                ui.notify("A senha deve ter pelo menos 8 caracteres, incluir uma letra maiúscula e um número.",
                          type="negative")
                return

            # tenta redefinir a senha no sql
            try:
                redefinir_senha_no_banco(token, new_password.value)
                ui.notify("✅ Senha redefinida com sucesso!", type="positive")
                ui.navigate.to("/")
            except ValueError as e:
                # token invalido ou expirado
                with ui.card().classes("absolute-center items-center").style("background-color: #f8d7da;"):
                    ui.label("⚠ Token inválido ou expirado!").classes("text-center text-h5 text-negative")
                    ui.label(
                        "O token fornecido é inválido ou já expirou. Clique em 'Gerar Novo Token'."
                    ).classes("text-center text-subtitle1 text-negative").style("margin-top: 10px;")

                    # botao para gerar novo token
                    ui.button(
                        "Novo Token",
                        on_click=lambda: ui.navigate.to("/recuperacao_senha"),
                        color="#008B8B"
                    ).classes("w-full").style("color: white; font-weight: bold; margin-top: 10px;")

                    # botao voltar ao inicio
                    ui.button(
                        "Voltar ao Início",
                        on_click=lambda: ui.navigate.to("/"),
                        color="red"
                    ).classes("w-full").style("color: white; font-weight: bold; margin-top: 10px;")
                return
            except mysql.connector.Error as e:
                ui.notify(f"❌ Erro ao redefinir senha: {e}", type="negative")

        # botao da interface
        ui.button("Redefinir Senha", on_click=redefinir_senha, color="#008B8B").classes("w-full").style(
            "color: white; font-weight: bold")
        ui.button("Voltar", on_click=lambda: ui.navigate.to("/"), color="#008B8B").classes("w-full").style(
            "color: white; font-weight: bold")



