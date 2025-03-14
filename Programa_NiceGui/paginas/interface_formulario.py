from datetime import date, timedelta
from nicegui import app, ui
from funcoes_menu import enviar_notificacao
from Programa_NiceGui.paginas.func_int_principal_form import salvar_ocorrencia
#from Programa_NiceGui.paginas.interface_principal import carregar_tabela
from db_conection import get_db_connection

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



# ------------------------------------------- ESTRUTURA FORMULARIO -------------------------------------------

def novo_formulario():
    app.add_static_files('/static', '../static')
    ui.add_head_html('<script src="/static/js/scripts.js"></script>')

    with ui.dialog() as dialog, ui.card().classes("w-4/5 h-[600px] mx-auto"):
        ui.label("Nova Ocorrência").classes("text-2xl mx-auto font-bold mb-4")

        with ui.row().classes("w-full justify-between"):
            with ui.grid(columns=2).classes("w-full"):
                cliente = ui.input("Cliente").classes("w-full")
                num_processo = ui.input("Nº Processo").classes("w-full")

        responsavel = ui.select(get_responsavel(), label="Responsável").classes("w-full")


        with ui.row().classes(" w-full justify-between"):
            with ui.grid(columns=2).classes("w-full"):
                with ui.input('Date') as date:
                    with ui.menu().props('no-parent-event') as menu:
                        with ui.date().bind_value(date).style(
                                "--q-primary:#008B8B; --q-color-calendar-header:#008B8B;"):
                            with ui.row().classes('justify-end'):
                                ui.button('Close', on_click=menu.close).props('flat').style("color:#008B8B;")
                    with date.add_slot('prepend'):
                        ui.icon('edit_calendar', color="#008B8B").on('click', menu.open).classes(
                            'cursor-pointer w-full')
                status = ui.input("Status", value="Em espera").props("readonly").classes("w-full")

        conteudo = ui.textarea("Conteúdo da ocorrência").props("maxlength=400").classes("w-full mr-2 mr-2")
        contador = ui.label("0/400 caracteres").classes("text-sm text-gray-500 mb-4")

        def atualizar_contador():
            carac_digitado = len(conteudo.value)
            contador.set_text(f"{carac_digitado}/400 caracteres")

            if carac_digitado >= 400:
                contador.classes(replace="text-sm text-red-500 mb-4")
            else:
                contador.classes(replace="text-sm text-gray-500 mb-4")

        # chama a atualizacao

        # conteudo.on("input", lambda: atualizar_contador())

        conteudo.on("keydown", lambda: atualizar_contador())
        conteudo.on("keyup", lambda: ())

        atualizar_contador()

        def btn_salvar():
            current_user_id = app.storage.user.get("userid", None)

            if not conteudo.value.strip(): #verifica se o campo esta vazio
                ui.notify("O campo 'Conteúdo da ocorrência' é obrigatório.", type="negative")
                return

            msg, sucesso = salvar_ocorrencia(cliente.value, num_processo.value, responsavel.value, date.value,
                                             status.value, conteudo.value)
            if sucesso:
                ui.notify(msg, type="positive")

                # Obtem todos os usuários (exceto o usuário logado) para enviar a notificação
                lista_user = obter_user()
                # chama a função: obter o nome do utilizador logado
                nome_user = obter_user_logado(current_user_id)

                if not nome_user:
                    ui.notify("Utilizador logado não encontrado.", type="negative")
                    return

                # Enviar a notificação para os usuários, excluindo o usuário logado
                for user in lista_user:
                    if user['id'] != current_user_id:
                        mensagem_notificacao = (
                            f"• <b>Nova ocorrência registrada por:</b><br>"
                            f"<span style='display: block; text-align: center;'>{nome_user}</span><br>"
                            f"• <b>Nome do cliente:</b> {cliente.value}<br>"
                            f"• <b>Nº Processo:</b> {num_processo.value}"
                        )
                        enviar_notificacao(user['id'], mensagem_notificacao)

                # Limpa os campos
                cliente.set_value("")
                num_processo.set_value("")
                responsavel.set_value(None)
                date.set_value(None)
                conteudo.set_value("")
                status.set_value("Em espera")

                # carregar_tabela()
                atualizar_contador()


            else:
                ui.notify(msg, type="negative")

        with ui.row().classes("mx-auto gap-x-8"):
            ui.button("Salvar", on_click=btn_salvar).style("color: white; font-weight: bold; "
                                    "background-color: #008B8B !important;").classes("btn-primary w-32")

            ui.button("Cancelar", on_click=dialog.close).style("color: white; font-weight: bold;"
                                    " background-color: #008B8B !important;").classes("btn-secondary w-32")

    dialog.open()

# ------------------------------------------- OBTEM O NOME DOS USERS -------------------------------------------


def obter_user():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """SELECT DISTINCT CONCAT (nome, ' ', apelido) as nome_completo, id FROM utilizador"""
    cursor.execute(query)
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users



# ------------------------------------------- OBTEM USER LOGADO -------------------------------------------

#busca o user logado para printar o nome na mensagem

def obter_user_logado(current_user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """SELECT CONCAT(nome, ' ', apelido) AS nome_completo FROM utilizador WHERE id = %s;"""
        cursor.execute(query, (current_user_id,))
        user = cursor.fetchone()
        if user:
            return user[0]  # Retorna o nome completo do utilizador
        return None
    finally:
        cursor.close()
        conn.close()










