from nicegui import ui, app
from datetime import datetime
from nicegui.elements.aggrid import AgGrid
from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection


# ------------------------------ BUSCA OCORRENCIAS ACEITAS ---------------------------

def buscar_ocorrencias_aceitas(usuario_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT id, cliente, num_processo, data, responsavel, status, titulo, conteudo
    FROM ocorrencias
    WHERE responsavel_id = %s
    """

    cursor.execute(query, (usuario_id,))
    ocorrencias = cursor.fetchall()
    conn.close()

    return [{
        "id": o[0],
        "cliente": o[1] if o[1] else "Sem cliente",
        "num_processo": o[2] if o[2] else "Sem número",
        "data": o[3].strftime("%d/%m/%Y") if isinstance(o[3], datetime) else "Sem data",
        "responsavel": o[4] if o[4] else "Desconhecido",
        "status": o[5] if o[5] else "Desconhecido",
        "titulo": o[6] if o[6] else "Sem título",
        "conteudo": o[7] if o[7] else "Sem conteúdo"
    } for o in ocorrencias] if ocorrencias else []


# ---------------------------------- CARREGA AS OCORRENCIAS  -------------------------------

def carregar_ocorrencias_user():
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
        ui.label("Nenhuma ocorrência atribuída!").classes("text-red-500 text-lg")
        return

        # Formatar a data para cada ocorrência
    for o in ocorrencias:
        # Verifica se o campo 'data' existe e não é None, e formata a data
        if o["data"] == "Sem data":
            o["data"] = "Data não informada"
        else:
            try:
                o["data"] = datetime.strptime(o["data"], "%Y-%m-%d").strftime("%d/%m/%Y")
            except ValueError:
                o["data"] = "Data inválida"

    global grid
    grid = ui.aggrid({
        "columnDefs": [
            {"headerName": "ID", "field": "id"},
            {"headerName": "Cliente", "field": "cliente"},
            {"headerName": "Nº Processo", "field": "num_processo"},
            {"headerName": "Status", "field": "status", "cellRenderer": "CustomButtonComponent"},
            {"headerName": "Título", "field": "titulo"},
            {"headerName": "Conteúdo", "field": "conteudo"},
            {"headerName": "Data", "field": "data"},
            {"headerName": "Ações", "field": "acoes", "cellRenderer": "htmlRenderer"}, # Placeholder (pois UI não pode ser passado para AgGrid)
        ],
        "rowData": ocorrencias,
    }).classes("w-full h-[500px] mx-auto") \
        .style(
        "background: transparent; border: 5px solid rgba(255, 255, 255, 0.5); overflow-x: auto; max-width: 100%; min-width: 300px;"
    )

    # botao auxiliar
    with ui.row().classes("mx-auto gap-x-10"):
        ui.button("Atualizar", on_click=lambda: carregar_ocorrencia()).style(
            "color: white; font-weight: bold;"
            " background-color: #008B8B !important;").classes("btn-secondary w-48")


def carregar_ocorrencia():
    """Atualiza a tabela sem precisar recriar a interface"""
    if grid:
        current_user_id = app.storage.user.get("userid", None)
        novas_ocorrencias = buscar_ocorrencias_aceitas(current_user_id)





