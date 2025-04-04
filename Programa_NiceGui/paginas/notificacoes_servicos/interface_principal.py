from attr import dataclass
from mysql.connector import cursor
from nicegui import app
from nicegui import ui
import Programa_NiceGui.paginas.interface_layout.global_state as global_state
from Programa_NiceGui.paginas.banco_dados.db_conection import obter_dados
from Programa_NiceGui.paginas.interface_layout.formulario import novo_formulario
from Programa_NiceGui.paginas.notificacoes_servicos.tabela import carregar_tabela
from nicegui.elements.aggrid import AgGrid
#import debugpy

# ----------------------------------------------- TABELA OCORRENCIA --------------------------------------------

def status_renderer(params):
    #Renderiza um select editável dentro da célula do AG Grid
    status_options = ["Em espera", "Em execução", "Concluído"]

    # Criar um dropdown UI dentro da célula
    with ui.row():
        select = ui.select(status_options, value=params["value"])

    return select

# ------------------------------------------- CONFIGURA O GRID --------------------------------------

def configurar_grid(novo_valor):
    global_state.grid = novo_valor  # Modifica a variável global

def obter_grid():
    return global_state.grid  # Retorna a variável global


def main_page():
    app.add_static_files('/static', '../static')
    ui.add_head_html('<link rel="stylesheet" type="text/css" href="/static/styles.css">')
    ui.add_head_html('<script src="/static/customButtonComponent.js"></script>')
    ui.add_head_html('<script src="/static/main.js"></script>')

    ui.label("Lista de Ocorrências").classes("text-4xl font-bold mb-4 mx-auto text-center")

    #(alteracoes feitas)
    #dados_banco = obter_dados()
    # Converte cada Row para dicionário antes de usar no AgGrid
    #dados_convertidos = [dict(row) for row in dados_banco]

    # Tabela de Ocorrências
    global grid
    grid = AgGrid({
        "columnDefs": [
            {"headerName": "ID", "field": "id"},
            {"headerName": "Cliente", "field": "cliente"},
            {"headerName": "Nº Processo", "field": "num_processo"},
            {"headerName": "Responsável", "field": "responsavel"},
            {"headerName": "Data", "field": "data"},
            {"headerName": "Status", "field": "status", "cellRenderer": "CustomButtonComponent"},
            {"headerName": "Título", "field": "titulo"},
            {"headerName": "Conteúdo", "field": "conteudo"},
            {"headerName": "Ações", "field": "acoes", "cellRenderer": "htmlRenderer"},
        ],
        "rowData": [],    #dados_convertidos,
    }).classes("w-full h-[500px] mx-auto") \
        .style(
        "background: transparent; border: 5px solid rgba(255, 255, 255, 0.5); overflow-x: auto; max-width: 100%; min-width: 300px;")

    #carregar_tabela(grid, usuario_logado)

    #configurar_grid(grid)

    usuario_logado = app.storage.user.get("username", None) # Obtém o usuário da sessão
    carregar_tabela(grid, usuario_logado)  # Passa para a função de carregamento


    # botoes auxiliares
    with ui.row().classes("mx-auto gap-x-10"):
        ui.button("Nova Ocorrência", on_click=novo_formulario).style("color: white; font-weight: bold;"
                        " background-color: #008B8B !important;").classes("btn-primary w-48")
        ui.button("Atualizar", on_click=lambda: carregar_tabela(grid, usuario_logado)).style("color: white; font-weight: bold;"
                        " background-color: #008B8B !important;").classes("btn-secondary w-48")

    div = ui.element('div').style("height: 100%")
    div._props['id'] = 'myGrid'

    carregar_tabela(grid, usuario_logado)
















