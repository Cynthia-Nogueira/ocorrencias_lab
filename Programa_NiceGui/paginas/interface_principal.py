from nicegui import app, ui
import mysql.connector
from nicegui.html import dialog

from Programa_NiceGui.paginas.func_int_principal_form import get_ocorrencias, excluir_ocorrencia, formulario_edicao, \
    update_ocorrencia
from Programa_NiceGui.paginas.interface_formulario import novo_formulario
from datetime import date, datetime


# ------------------------------------- Conexão com Banco de Dados -------------------------------------


def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="senha",
        database="seu_banco"
    )

# --------------------------------------------------- EXCLUI A OCORRENCIA DA TABELA ---------------------------------------


def confirmar_exclusao(id, num_processo):
    dialog = ui.dialog()
    with dialog:
        with ui.card():
            ui.label(f"Tem certeza que deseja excluir a ocorrência do processo: {num_processo}?")
            with ui.row().classes("mt4"):
                ui.button("Cancelar", on_click=dialog.close, color="#B22222").classes("btn-secondary")
                ui.button("Confirmar", on_click=lambda: [excluir_ocorrencia(dialog, id), carregar_tabela()],
                          color="#008B8B").classes("btn-primary")

    dialog.open()

# --------------------------------------------------- CARREGA A TABELA ---------------------------------------


# carrega os dados na tabela
def carregar_tabela():
    dados_tabela = []

    try:
        for ocorrencia in get_ocorrencias():
            id_, cliente, num_processo, responsavel, data, status, conteudo = ocorrencia

            # Botões para edição e exclusão (com confirmação)
            botoes = f"""
                <button onclick="formulario_edicao({id_})" class='btn-primary'>Editar</button>
                <button onclick="confirmar_exclusao_gui({id_}, '{num_processo}')" class='btn-secondary ml-2'>Excluir</button>          
            """

            # Adiciona os dados para a tabela
            dados_tabela.append({
                "id": id_,
                "cliente": cliente,
                "num_processo": num_processo,
                "responsavel": responsavel,
                "data": data,
                "status": status,
                "conteudo": conteudo,
                "acoes": botoes,
            })

        # Atualiza os dados na tabela
        grid.options["rowData"] = dados_tabela
        grid.update()

    except Exception as e:
        # Exibe o erro caso ocorra algo inesperado
        ui.notify(f"Erro ao carregar a tabela: {e}", color="red")


# ----------------------------------------------- TABELA OCORRENCIA --------------------------------------------


def main_page():
    app.add_static_files('/static', '../static')
    ui.add_head_html('<link rel="stylesheet" type="text/css" href="/static/styles.css">')

    ui.label("Lista de Ocorrências").classes("text-4xl font-bold mb-4 mx-auto text-center")

    # Tabela de Ocorrências
    global grid
    grid = ui.aggrid({
        "columnDefs": [
            {"headerName": "ID", "field": "id"},
            {"headerName": "Cliente", "field": "cliente"},
            {"headerName": "Nº Processo", "field": "num_processo"},
            {"headerName": "Responsável", "field": "responsavel"},
            {"headerName": "Data", "field": "data"},
            {"headerName": "Status", "field": "status"},
            {"headerName": "Conteúdo", "field": "conteudo"},
            {"headerName": "Ações", "field": "acoes", "cellRenderer": "htmlRenderer"},
        ],
        "rowData": [],
    }).classes("w-full max-w-[1200px] h-[500px] mx-auto") \
        .style("background: transparent; border: 5px solid rgba(255, 255, 255, 0.5);")

    # botoes auxiliares
    with ui.row().classes("mx-auto gap-x-10"):
        ui.button("Nova Ocorrência", on_click=novo_formulario, color="#008B8B") \
            .classes("btn-primary w-48").style("color: white; font-weight: bold")
        ui.button("Atualizar", on_click=carregar_tabela, color="#008B8B") \
            .classes("btn-secondary w-48").style("color: white; font-weight: bold")


    carregar_tabela()











