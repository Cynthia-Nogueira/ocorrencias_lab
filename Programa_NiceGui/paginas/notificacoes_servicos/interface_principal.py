from nicegui import app
from nicegui import ui
import Programa_NiceGui.paginas.interface_layout.global_state as global_state
from Programa_NiceGui.paginas.interface_layout.formulario import novo_formulario
from Programa_NiceGui.paginas.notificacoes_servicos.tabela import carregar_tabela
from nicegui.elements.aggrid import AgGrid

# ------------------------------------- TABELA OCORRENCIA  (SEM USO) ------------------------------------

def status_renderer(params):
    #Renderiza um select editável dentro da célula do AG Grid
    status_options = ["Em espera", "Em execução", "Concluída", "Devolvida", "Não atribuída", "Cancelada"]

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
    ui.add_head_html('<script src="/static/main.js"></script>')

    ui.label("Lista de Ocorrências").classes("text-4xl font-bold mb-4 mx-auto text-center")

    # Tabela de Ocorrências
    global grid
    grid = AgGrid({
        "columnDefs": [
            {"headerName": "Data", "field": "data"},
            {"headerName": "Cliente", "field": "cliente"},
            {"headerName": "Nº Processo", "field": "num_processo"},
            {"headerName": "Responsável", "field": "responsavel"},
            {"headerName": "Status", "field": "status"},
            {"headerName": "Título", "field": "titulo"},
            {"headerName": "Conteúdo", "field": "conteudo", "cellRenderer": "conteudoCellRenderer"},
        ],
        "rowData": [],
        "defaultColDef": {
            "resizable": True,
            "sortable": True,
            "filter": True,
            "flex": 1,
            "minWidth": 100,
            "cellClass": "cell-wrap-text",  # Permiti quebra de texto
        },
        "onCellClicked": "handleCellClick(event)",  #Adiciona handler de clique
        "suppressCellSelection": True, }).classes("w-full h-[500px] mx-auto").style(
        "background: transparent; border: 5px solid rgba(255, 255, 255, 0.5); overflow-x: auto; max-width: 100%; min-width: 300px;")

    # Adiciona o JavaScript necessário
    ui.add_head_html(f"""
    <script>
        // Função para renderizar o conteúdo com limite de caracteres
        function conteudoCellRenderer(params) {{
            const maxLength = 50;
            const content = params.value || '';
            return content.length > maxLength 
                ? content.substring(0, maxLength) + '...' 
                : content;
        }}

        // Handler para clique na célula
        function handleCellClick(event) {{
            if (event.column.colId === 'conteudo') {{
                const rowData = event.data;
                // Envia os dados para o Python via websocket
                socket.send(JSON.stringify({{
                    'type': 'cell_clicked',
                    'data': rowData
                }}));
            }}
        }}
    </script>
    """)

    usuario_logado = app.storage.user.get("username", None)
    carregar_tabela(grid, usuario_logado)

    # botoes auxiliares
    with ui.row().classes("mx-auto gap-x-10"):
        ui.button("Nova Ocorrência", on_click=novo_formulario).style(
            "color: white; font-weight: bold; background-color: #008B8B !important;"
        ).classes("btn-primary w-48")

        ui.button("Atualizar", on_click=lambda: carregar_tabela(grid, usuario_logado)).style(
            "color: white; font-weight: bold; background-color: #008B8B !important;"
        ).classes("btn-secondary w-48")
