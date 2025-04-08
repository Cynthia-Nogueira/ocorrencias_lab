from nicegui import ui, app
from datetime import datetime, timedelta
#from nicegui.elements.aggrid import AgGrid
from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection
from Programa_NiceGui.paginas.interface_layout.ocorrencias_vencidas import feriados_portugal, horas_uteis


# ------------------------------ BUSCA OCORRENCIAS ACEITAS ---------------------------

def buscar_ocorrencias_aceitas(usuario_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
        SELECT id, cliente, num_processo, data, responsavel, status, titulo, conteudo, data_aceite
        FROM ocorrencias
        WHERE responsavel_id = %s
        """

        cursor.execute(query, (usuario_id,))
        ocorrencias = cursor.fetchall()

        # Obter os feriados do ano atual
        ano_atual = datetime.now().year
        feriados = feriados_portugal(ano_atual)

        resultado = []

        for o in ocorrencias:
            # verifica se a ocorrência foi aceita há mais de 48 horas
            id_ocorrencia, cliente, num_processo, data, responsavel, status, titulo, conteudo, data_aceite = o

            if data_aceite:
                # converte para datetime
                data_aceite = datetime.strptime(str(data_aceite), "%Y-%m-%d %H:%M:%S")
                agora = datetime.now()

                # Calcular as horas úteis passadas
                horas_passadas = horas_uteis(data_aceite, agora, feriados)

                # Se passaram mais de 48h, muda o status para "Não Atribuída"
                if horas_passadas > 48 and status == "Em espera":
                    # Atualiza o status para "Não Atribuída"
                    update_query = """
                    UPDATE ocorrencias
                    SET status = 'Não Atribuída', responsavel_id = NULL, data_aceite = NULL
                    WHERE id = %s
                    """
                    cursor.execute(update_query, (id_ocorrencia,))
                    conn.commit()

                    status = "Não Atribuída"

            # Adiciona ao resultado final
            resultado.append({
                "id": id_ocorrencia,
                "cliente": cliente if cliente else "Sem cliente",
                "num_processo": num_processo if num_processo else "Sem número",
                "data": data.strftime("%d/%m/%Y") if isinstance(data, datetime) else "Sem data",
                "responsavel": responsavel if responsavel else "Responsável vázio",
                "status": status if status else "Desconhecido",
                "titulo": titulo if titulo else "Sem título",
                "conteudo": conteudo if conteudo else "Sem conteúdo"
            })

        return resultado if resultado else []

    finally:
        cursor.close()
        conn.close()

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

    #renderiza a tabela

    if not ocorrencias:
        ocorrencias = [{
            "id": "",
            "cliente": "",
            "num_processo": "",
            "data": "",
            "responsavel": "",
            "status": "",
            "titulo": "",
            "conteudo": ""
        }]

    if not ocorrencias:
        ui.label("Nenhuma ocorrência atribuída!").classes("text-red-500 text-lg")
        return

        # Formatar a data para cada ocorrência
    for o in ocorrencias:
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
    }).classes("w-full h-[500px] mx-auto").style("background: transparent; border: 5px solid "
              "rgba(255, 255, 255, 0.5); overflow-x: auto; max-width: 100%; min-width: 300px;")

    # botao auxiliar
    with ui.row().classes("mx-auto gap-x-10"):
        ui.button("Atualizar", on_click=lambda: carregar_ocorrencia()).style(
            "color: white; font-weight: bold;"
            " background-color: #008B8B !important;").classes("btn-secondary w-48")

# ---------------------------------- ATUALIZA A TABELA OCORRENCIAS  -------------------------------

def carregar_ocorrencia():
    global grid  # está acessando o grid globalmente

    if grid:
        current_user_id = app.storage.user.get("userid", None)
        novas_ocorrencias = buscar_ocorrencias_aceitas(current_user_id)

        grid.set_data(novas_ocorrencias)  # Atualizando a tabela com a nova lista de dados









