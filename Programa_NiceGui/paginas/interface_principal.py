from nicegui import app, ui

from nicegui.html import dialog

from Programa_NiceGui.paginas.func_int_principal_form import formulario_edicao
from func_int_principal_form import get_ocorrencias, excluir_ocorrencia
from Programa_NiceGui.paginas.interface_formulario import novo_formulario
from datetime import date, datetime
from nicegui import ui
from flask import session
from db_conection import get_db_connection
from nicegui.elements.aggrid import AgGrid


# --------------------------------------------------- CARREGA A TABELA ---------------------------------------

def atualizar_tabela(dados_tabela):
    # Atualiza os dados na tabela
    grid.options["rowData"] = dados_tabela
    grid.update()


# ------------------------ carrega os dados na tabela---------------------

def carregar_tabela(usuario_logado):
    """Carrega os dados das ocorrências na tabela, considerando o usuário logado."""
    dados_tabela = []

    try:
        for ocorrencia in get_ocorrencias():
            id_, cliente, num_processo, responsavel, data, status, conteudo = ocorrencia

            # Se o usuário logado for o responsável, exibe um select editável
            if usuario_logado == responsavel:
                status_select = f"""
                    <select id='status_{id_}' onchange='atualizarStatus({id_})' class='status-select'>
                        <option value="Em espera" {"selected" if status == "Em espera" else ""}>Em espera</option>
                        <option value="Em execução" {"selected" if status == "Em execução" else ""}>Em execução</option>
                        <option value="Concluído" {"selected" if status == "Concluído" else ""}>Concluído</option>
                    </select>
                """
            else:
                # Se não for o responsável, mostra apenas o status como texto
                status_select = f"<span>{status}</span>"

            # Botões de ação
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
                "status": status_select,
                "conteudo": conteudo,
                "acoes": botoes,
            })

        # Atualiza a tabela com os dados carregados
        atualizar_tabela(dados_tabela)

    except Exception as e:
        ui.notify(f"Erro ao carregar a tabela: {e}", color="red")


# ----------------------------------------------- TABELA OCORRENCIA --------------------------------------------

def status_renderer(params):
    """Renderiza um select editável dentro da célula do AG Grid"""
    status_options = ["Em espera", "Em execução", "Concluído"]

    # Criar um dropdown UI dentro da célula
    with ui.row():
        select = ui.select(status_options, value=params["value"])

    return select

def main_page():
    app.add_static_files('/static', '../static')
    ui.add_head_html('<link rel="stylesheet" type="text/css" href="/static/styles.css">')
    ui.add_head_html('<script src="/static/scripts.js"></script>')

    ui.label("Lista de Ocorrências").classes("text-4xl font-bold mb-4 mx-auto text-center")

    # Tabela de Ocorrências
    global grid
    grid = AgGrid({
        "columnDefs": [
            {"headerName": "ID", "field": "id"},
            {"headerName": "Cliente", "field": "cliente"},
            {"headerName": "Nº Processo", "field": "num_processo"},
            {"headerName": "Responsável", "field": "responsavel"},
            {"headerName": "Data", "field": "data"},
                {"headerName": "Status", "field": "status", "cellRenderer": "statusRenderer"},
            {"headerName": "Conteúdo", "field": "conteudo"},
            {"headerName": "Ações", "field": "acoes", "cellRenderer": "htmlRenderer"},
        ],
        "rowData": [],
    }).classes("w-full max-w-[1200px] h-[500px] mx-auto") \
        .style("background: transparent; border: 5px solid rgba(255, 255, 255, 0.5);")

    usuario_logado = app.storage.user.get("username", None) # Obtém o usuário da sessão
    carregar_tabela(usuario_logado)  # Passa para a função de carregamento

    # botoes auxiliares
    with ui.row().classes("mx-auto gap-x-10"):
        ui.button("Nova Ocorrência", on_click=novo_formulario, color="#008B8B") \
            .classes("btn-primary w-48").style("color: white; font-weight: bold")
        ui.button("Atualizar", on_click=carregar_tabela, color="#008B8B") \
            .classes("btn-secondary w-48").style("color: white; font-weight: bold")


    carregar_tabela(usuario_logado)














