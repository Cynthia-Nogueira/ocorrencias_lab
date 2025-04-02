from nicegui import ui, app
from nicegui.elements.aggrid import AgGrid
from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection


# ------------------------------ BUSCA OCORRENCIAS ACEITAS ---------------------------

def buscar_ocorrencias_aceitas(usuario_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT id, cliente, num_processo, status
    FROM ocorrencias
    WHERE responsavel = %s
    """

    cursor.execute(query, (usuario_id,))
    ocorrencias = cursor.fetchall()
    conn.close()

    return [{"id": o[0], "cliente": o[1], "num_processo": o[2], "status": o[3]} for o in ocorrencias]


# ---------------------------------- ATUALIZA STATUS DA OCORRENCIAS  -------------------------------

def atualizar_status(ocorrencia_id, novo_status):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "UPDATE ocorrencias SET status = %s WHERE id = %s"
    cursor.execute(query, (novo_status, ocorrencia_id))
    conn.commit()
    conn.close()

    ui.notify(f"Status atualizado para {novo_status}!", type="success")

    # Atualiza somente a tabela, sem recarregar toda a página
    carregar_tabela()


# ---------------------------------- CARREGA AS OCORRENCIAS  -------------------------------

def carregar_ocorrencias():
    app.add_static_files('/static', '../static')
    ui.add_head_html('<link rel="stylesheet" type="text/css" href="/static/styles.css">')
    ui.add_head_html('<script src="/static/customButtonComponent.js"></script>')
    ui.add_head_html('<script src="/static/main.js"></script>')

    ui.label("Ocorrências Atribuídas").classes("text-4xl font-bold mb-4 mx-auto text-center")

    current_user_id = app.storage.user.get("userid", None)
    if not current_user_id:
        ui.label("Erro: Usuário não encontrado.").classes("text-red-500 text-lg")
        return

    ocorrencias = buscar_ocorrencias_aceitas(current_user_id)

    if not ocorrencias:
        ui.label("Nenhuma ocorrência encontrada!").classes("text-red-500 text-lg")
        return

    global grid
    grid = AgGrid({
        "columnDefs": [
            {"headerName": "ID", "field": "id"},
            {"headerName": "Cliente", "field": "cliente"},
            {"headerName": "Nº Processo", "field": "num_processo"},
            {"headerName": "Status", "field": "status", "cellRenderer": "CustomButtonComponent"},
        ],
        "rowData": ocorrencias,
    }).classes("w-full h-[500px] mx-auto") \
        .style(
        "background: transparent; border: 5px solid rgba(255, 255, 255, 0.5); overflow-x: auto; max-width: 100%; min-width: 300px;"
    )

    carregar_tabela(grid)


def carregar_tabela():
    """Atualiza a tabela sem precisar recriar a interface"""
    if grid:
        current_user_id = app.storage.user.get("userid", None)
        novas_ocorrencias = buscar_ocorrencias_aceitas(current_user_id)
        grid.update_data(novas_ocorrencias)


# ---------------------------------- MOSTRA OS DETALHES DAS OCORRENCIAS  -------------------------------

def abrir_detalhes(ocorrencia):
    with ui.dialog() as modal:
        with ui.card():
            ui.label(f"📌 Ocorrência: {ocorrencia['num_processo']}")
            ui.label(f"👤 Cliente: {ocorrencia['cliente']}")
            ui.label(f"📌 Status Atual: {ocorrencia['status']}")
            ui.label(f"🗒️ Conteúdo: {ocorrencia.get('conteudo', 'Sem conteúdo disponível')}")

            with ui.row():
                ui.button("Em Espera", on_click=lambda: atualizar_status(ocorrencia['id'], 'Em Espera'))
                ui.button("Concluído", on_click=lambda: atualizar_status(ocorrencia['id'], 'Concluído'))

            ui.button("Fechar", on_click=modal.close)

    modal.open()


