from datetime import date, timedelta
from nicegui import app, ui
from Programa_NiceGui.paginas.func_int_principal_form import salvar_ocorrencia, get_db_connection


# ------------------------------------- SELECT RESPONSAVEL ----------------------------------------

def get_responsavel():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM responsaveis")

    responsaveis = [row[0] for row in cursor.fetchall()]  # transforma os resultados em uma lista de nomes
    cursor.close()
    conn.close()
    return responsaveis

# ------------------------------------------ DATAS --------------------------------------------


# ------------------------------------- ESTRUTURA FORMULARIO ----------------------------------------

def novo_formulario():
    app.add_static_files('/static', '../static')

    with ui.dialog() as dialog, ui.card():
        ui.label("Nova Ocorrência").classes("text-2xl text-center font-bold mb-4")

        with ui.row().classes("justify-between"):
            with ui.grid(columns=2):
                cliente = ui.input("Cliente").classes("w-full")
                num_processo = ui.input("Nº Processo").classes("w-full")

        with ui.grid(columns=1):
            responsavel = ui.select(get_responsavel(), label="Responsável").classes("w-full")

        with ui.row().classes("justify-between"):
            with ui.grid(columns=2):
                data_select = ui.date(value=date.today()).classes("w-full")
                status = ui.input("Status", value="Em espera").props("readonly").classes("w-full")

        conteudo = ui.textarea("Conteúdo da ocorrência").classes("w-full mr-2")

        with ui.row().classes("mx-auto gap-x-8"):
            ui.button("Salvar", on_click=lambda: salvar_ocorrencia(
                cliente.value,
                num_processo.value,
                responsavel.value,
                data_select.value,
                status.value,
                conteudo.value
            ), color="#008B8B").classes("btn-primary w-32").style("color: white; font-weight: bold")

            ui.button("Cancelar", on_click=dialog.close, color="#008B8B").classes("btn-secondary w-32").style("color: white; font-weight: bold")

    dialog.open()














