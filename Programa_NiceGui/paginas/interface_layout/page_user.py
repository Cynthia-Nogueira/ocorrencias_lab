from nicegui import ui, app
from datetime import datetime
from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection
from Programa_NiceGui.paginas.interface_layout.ocorrencias_vencidas import feriados_portugal, horas_uteis
from Programa_NiceGui.paginas.notificacoes_servicos.helper_notificacoes import formatar_data_para_interface
from Programa_NiceGui.paginas.notificacoes_servicos.tabela import atualizar_tabela

# ------------------------------ BUSCA OCORRENCIAS ACEITAS ---------------------------

def buscar_ocorrencias_aceitas(usuario_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
        SELECT 
            id, cliente, num_processo, responsavel, responsavel_id,
            data_status_alterado AS data, status, titulo, conteudo, criador_id
        FROM 
            ocorrencias
        WHERE 
            responsavel_id = %s
        ORDER BY 
            data_status_alterado DESC;
        """

        cursor.execute(query, (usuario_id,))
        ocorrencias = cursor.fetchall()

        # Obter os feriados do ano atual
        feriados = feriados_portugal()

        resultado = []

        for o in ocorrencias:
            # verifica se a ocorrência foi aceita há mais de 48 horas
            id_ocorrencia, cliente, num_processo, responsavel, responsavel_id, data, status, titulo, conteudo, criador_id = o

            data_aceite = data

            if data_aceite:
                # converte para datetime
                data_aceite = datetime.strptime(str(data_aceite), "%Y-%m-%d %H:%M:%S")
                agora = datetime.now()
                horas_passadas = horas_uteis(data_aceite, agora, feriados)

                # Se passaram mais de 48h, muda o status para "Expirada"
                if horas_passadas.total_seconds() / 3600 > 48 and status == "Em espera":
                    # Atualiza o status para "Expirada"
                    update_query = """
                    UPDATE ocorrencias
                    SET status = 'Expirada', responsavel_id = NULL, data_aceite = NULL
                    WHERE id = %s
                    """
                    cursor.execute(update_query, (id_ocorrencia,))
                    conn.commit()

                    status = "Expirada"

            # Adiciona ao resultado final
            resultado.append({
                "id": id_ocorrencia,
                "cliente": cliente if cliente else "Sem cliente",
                "num_processo": num_processo if num_processo else "Sem número",
                "data": formatar_data_para_interface(data_aceite),
                "responsavel": responsavel if responsavel else "Responsável vázio",
                "status": status if status else "Desconhecido",
                "titulo": titulo if titulo else "Sem título",
                "conteudo": conteudo if conteudo else "Sem conteúdo",
                "criador_id": criador_id if criador_id else "Não encontrado",
            })

        return resultado if resultado else []

    finally:
        cursor.close()
        conn.close()

# ---------------------------------- CARREGA AS OCORRENCIAS  -------------------------------

def carregar_ocorrencias_user():
    app.add_static_files('/static', '../static')
    ui.add_head_html('<link rel="stylesheet" type="text/css" href="/static/styles.css">')
    ui.add_head_html('<script src="/static/main.js"></script>')

    global grid

    ui.label("Ocorrências Atribuídas").classes("text-4xl font-bold mb-4 mx-auto text-center")

    current_user_id = app.storage.user.get("userid", None)

    if not current_user_id:
        ui.label("Erro: Usuário não encontrado.").classes("text-red-500 text-lg")
        return

    ocorrencias_acete = buscar_ocorrencias_aceitas(current_user_id)
    ocorrencias = ocorrencias_acete or []

    for o in ocorrencias_acete:
        if o["data"] == "Sem data":
            o["data"] = "Data não informada"

    #renderiza a tabela
    if not ocorrencias_acete:
        ocorrencias = [{
            "id": "",
            "cliente": "",
            "num_processo": "",
            "responsavel": "",
            "data": "",
            "status": "",
            "titulo": "",
            "conteudo": ""
        }]

    if not ocorrencias:
        ui.label("Nenhuma ocorrência atribuída!").classes("text-red-500 text-lg")
        return

    for o in ocorrencias:
        if o["data"] == "Sem data":
            o["data"] = "Data não informada"

    grid = ui.aggrid({
        "columnDefs": [
            {"headerName": "Data", "field": "data"},
            {"headerName": "Cliente", "field": "cliente"},
            {"headerName": "Nº Processo", "field": "num_processo"},
            {"headerName": "Responsável", "field": "responsavel"},
            {"headerName": "Status", "field": "status"},
            {"headerName": "Título", "field": "titulo"},
            {"headerName": "Conteúdo", "field": "conteudo"},
        ],
        "rowData": ocorrencias,
    }).classes("w-full h-[500px] mx-auto").style("background: transparent; border: 5px solid "
              "rgba(255, 255, 255, 0.5); overflow-x: auto; max-width: 100%; min-width: 300px;")

    atualizar_tabela(grid, ocorrencias_acete)

    # Botão de atualizar
    with ui.row().classes("mx-auto gap-x-10"):
        ui.button("Atualizar",
                  on_click=lambda: atualizar_tabela(grid, buscar_ocorrencias_aceitas(current_user_id))).style(
            "color: white; font-weight: bold; background-color: #008B8B !important;"
             ).classes("btn-secondary w-48")

# ---------------------------------- ATUALIZA A TABELA OCORRENCIAS  -------------------------------

def carregar_ocorrencia():
    global grid  # acessa o grid globalmente

    if grid:
        current_user_id = app.storage.user.get("userid", None)
        novas_ocorrencias = buscar_ocorrencias_aceitas(current_user_id)

        grid.set_data(novas_ocorrencias)  # atualiza a tabela









