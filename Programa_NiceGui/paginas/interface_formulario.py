from datetime import date, timedelta
from nicegui import app, ui
from Programa_NiceGui.paginas.func_int_principal_form import salvar_ocorrencia
#from Programa_NiceGui.paginas.interface_principal import carregar_tabela
from db_conection import get_db_connection

# ------------------------------------- SELECT RESPONSAVEL ----------------------------------------

def get_responsavel():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT CONCAT(nome, ' ', apelido) AS nome_completo FROM utilizador;")

    responsaveis = [row[0] for row in cursor.fetchall()]  # transforma os resultados em uma lista de nomes
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

        with ui.row().classes("w-full"):
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
            if not conteudo.value.strip():  # Verifica se o campo conteúdo está vazio
                ui.notify("O campo 'Conteúdo da ocorrência' é obrigatório.", type="negative")
                return

            msg, sucesso = salvar_ocorrencia(cliente.value, num_processo.value, responsavel.value, date.value,
                                             status.value, conteudo.value)
            if sucesso:
                ui.notify(msg, type="positive")

                # Limpa os campos
                cliente.set_value("")
                num_processo.set_value("")
                responsavel.set_value(None)
                date.set_value(None)
                conteudo.set_value("")
                status.set_value("Em espera")

                atualizar_contador()
                #carregar_tabela()

            else:
                ui.notify(msg, type="negative")

        with ui.row().classes("mx-auto gap-x-8"):
            ui.button("Salvar", on_click=btn_salvar, color="#008B8B").classes("btn-primary w-32").style(
                "color: white; font-weight: bold")

            ui.button("Cancelar", on_click=dialog.close, color="#008B8B").classes("btn-secondary w-32").style(
                "color: white; font-weight: bold")


    dialog.open()
















