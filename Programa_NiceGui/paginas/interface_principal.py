from nicegui import app, ui
import mysql.connector
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


# ----------------------------------------------- TABELA OCORRENCIA --------------------------------------------


def main_page():
    app.add_static_files('/static', '../static')
    ui.add_head_html('<link rel="stylesheet" type="text/css" href="/static/styles.css">')

    ui.label("Lista de Ocorrências").classes("text-3xl font-bold mb-4 text-center")

    # Tabela de Ocorrências
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
    }).classes("w-full")

    # carrega os dados na tabela
    def carregar_tabela():
        dados_tabela = []

        for ocorrencia in get_ocorrencias():
            id_, cliente, num_processo, responsavel, data, status, conteudo = ocorrencia

            botoes = f"""
                <button onclick="formulario_edicao({id_})" class='btn-primary'>Editar</button>
                <button onclick="excluir_ocorrencia({id_})" class='btn-secondary ml-2'>Excluir</button>          
            """   #colocar mensagem perguntando se tem certeza que deseja excluir

            dados_tabela.append({
                "id": id_,
                "cliente": cliente,
                "num_processo": num_processo,
                "responsavel": responsavel,
                "data": data,
                "status": status,
                "conteudo": conteudo,
                "acoes": botoes
            })

        grid.options["rowData"] = dados_tabela
        grid.update()

    # botoes auxiliares
    with ui.row().classes("mx-auto gap-x-10"):
        ui.button("Nova Ocorrência", on_click=novo_formulario, color="#008B8B").classes("btn-primary w-48").style("color: white; font-weight: bold")
        ui.button("Atualizar", on_click=carregar_tabela, color="#008B8B").classes("btn-secondary w-48").style("color: white; font-weight: bold")

    # carrega a tabela ao abrir a pag
    carregar_tabela()









