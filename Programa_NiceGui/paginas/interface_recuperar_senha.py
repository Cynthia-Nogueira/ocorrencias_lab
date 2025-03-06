import re
import bcrypt
"""
from Programa_NiceGui.paginas.send_email import sendmail
import interface_login_cadastro
from interface_token import gerar_token, redefinir_senha_no_banco
from nicegui import app, ui
"""
from send_email import sendmail
from nicegui import app, ui
from db_conection import get_db_connection

#----------------------------------------------- encripta a senha ---------------------------------------------------


def hash_senha(senha: str) -> str:

    # gera o hash da senha usando bcrypt
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(senha.encode(), salt).decode()


#------------------------------------------- Recuperar senha page -----------------------------------------------------

def recuperar_senha_page():
    app.add_static_files('/static', '../static')
    ui.add_head_html('<link rel="stylesheet" type="text/css" href="/static/styles.css">')

    with ui.card().classes("absolute-center items-center").style("background-color: #d2e9dd; width: 400px; height: 250px; border-radius: 12px;"):
        ui.label("Digite seu e-mail").classes("text-h4 text- mx-auto")

        email = ui.input("E-mail").classes("w-full")

        # verifica se o email foi preenchido
        def enviar_link():
            if not email.value:
                ui.notify("Preencha o campo com seu e-mail!", type="negative")
                return

            # Valida o e-mail
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
                    # Envia o link fixo para o e-mail
                    sendmail(email.value)
                    ui.notify(f"O link para redefinição foi enviado para o e-mail {email.value}!", type="positive")
                else:
                    ui.notify("E-mail não encontrado!", type="negative")

            except Exception as e:
                ui.notify(f"Erro ao processar: {e}", type="negative")
            finally:
                cursor.close()
                conn.close()

        ui.button("Enviar Link", on_click=enviar_link, color="#008B8B").classes("w-full").style(
            "color: white; font-weight: bold")
        ui.button("Voltar", on_click=lambda: ui.navigate.to("/"), color="#008B8B").classes("w-full").classes("w-full").style("color: white; font-weight: bold")



# ------------------------------------------------ Redefinição de senha ------------------------------------------------

def redefinir_senha_page():
    app.add_static_files('/static', '../static')
    ui.add_head_html('<link rel="stylesheet" type="text/css" href="/static/styles.css">')

    with ui.card().classes("absolute-center items-center").style("background-color: #d2e9dd; width: 380px; height: 400px;"):
        ui.label("Redefinir Senha").classes("text-h4 text-center")

        email = ui.input("E-mail").classes("w-full")
        new_password = ui.input("Nova Senha", password=True, password_toggle_button=True).classes("w-full")
        confirm_new_password = ui.input("Confirmar Senha", password=True, password_toggle_button=True).classes("w-full")

        def redefinir_senha():
            if not email.value or not new_password.value or not confirm_new_password.value:
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

            conn = get_db_connection()
            cursor = conn.cursor()

            try:
                # Verifica se o e-mail existe no banco
                cursor.execute("SELECT username FROM utilizador WHERE email = %s", (email.value,))
                result = cursor.fetchone()

                if result:
                    # Redefine a senha no banco
                    senha_hash = hash_senha(new_password.value)
                    cursor.execute("UPDATE utilizador SET password = %s WHERE email = %s", (senha_hash, email.value))
                    conn.commit()

                    ui.notify("✅ Senha redefinida com sucesso!", type="positive")
                    ui.navigate.to("/")
                else:
                    ui.notify("E-mail não encontrado!", type="negative")
            except Exception as e:
                ui.notify(f"Erro ao redefinir senha: {e}", type="negative")
            finally:
                cursor.close()
                conn.close()

        ui.button("Redefinir Senha", on_click=redefinir_senha, color="#008B8B").classes("w-full").style(
            "color: white; font-weight: bold")
        ui.button("Voltar", on_click=lambda: ui.navigate.to("/"), color="#008B8B").classes("w-full").style(
            "color: white; font-weight: bold")



