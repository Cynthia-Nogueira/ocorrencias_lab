from nicegui import ui, app
from datetime import datetime
from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection
from Programa_NiceGui.paginas.interface_layout.ocorrencias_vencidas import feriados_portugal, horas_uteis

# ------------------------------ BUSCA OCORRENCIAS ACEITAS ---------------------------

def buscar_ocorrencias_aceitas(usuario_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
        SELECT 
            o.id,
            o.cliente,
            o.num_processo,
            u.nome as responsavel,
            o.responsavel_id,
            o.data_status_alterado AS data,
            o.status,
            o.titulo,
            o.conteudo,
            o.criador_id
        FROM 
            ocorrencias o
        LEFT JOIN 
            utilizador u ON o.responsavel_id = u.id
        WHERE 
            o.responsavel_id = %s
        ORDER BY 
            o.data_status_alterado DESC;
        """

        cursor.execute(query, (usuario_id,))
        ocorrencias = cursor.fetchall()

        feriados = feriados_portugal()
        resultado = []

        for o in ocorrencias:
            id_ocorrencia, cliente, num_processo, responsavel, responsavel_id, data, status, titulo, conteudo, criador_id = o

            data_aceite = data
            status_atualizado = status

            if data_aceite:
                try:
                    data_aceite = datetime.strptime(str(data_aceite), "%Y-%m-%d %H:%M:%S")
                    agora = datetime.now()
                    horas_passadas = horas_uteis(data_aceite, agora, feriados)

                    if horas_passadas.total_seconds() / 3600 > 48 and status == "Em espera":
                        cursor.execute("""
                            UPDATE ocorrencias
                            SET status = 'Expirada', responsavel_id = NULL, data_aceite = NULL
                            WHERE id = %s
                        """, (id_ocorrencia,))
                        conn.commit()
                        status_atualizado = "Expirada"
                except ValueError as e:
                    print(f"Erro ao processar data: {e}")

            resultado.append({
                "id": id_ocorrencia,
                "cliente": cliente or "Sem cliente",
                "num_processo": num_processo or "Sem número",
                "responsavel": responsavel or "Não atribuído",
                "responsavel_id": responsavel_id,
                "data": data_aceite.strftime("%d/%m/%Y %H:%M") if isinstance(data_aceite, datetime) else "Sem data",
                "status": status_atualizado or "Desconhecido",
                "titulo": titulo or "Sem título",
                "conteudo": conteudo or "Sem conteúdo",
                "criador_id": criador_id
            })

        return resultado

    except Exception as e:
        ui.notify(f"Erro ao buscar ocorrências: {str(e)}", type='negative')
        return []
    finally:
        cursor.close()
        conn.close()

# ---------------------------------- CARREGA AS OCORRENCIAS  -------------------------------

def carregar_ocorrencias_user():
    from Programa_NiceGui.paginas.interface_layout.menu import detalhes_ocorrencia
    app.add_static_files('/static', '../static')
    ui.add_head_html('<link rel="stylesheet" type="text/css" href="/static/styles.css">')
    ui.add_head_html('<script src="/static/main.js"></script>')

    global grid

    ui.label("Ocorrências Atribuídas").classes("text-4xl font-bold mb-4 mx-auto text-center")

    current_user_id = app.storage.user.get("userid", None)

    if not current_user_id:
        ui.label("Erro: Usuário não encontrado.").classes("text-red-500 text-lg")
        return

    ocorrencias_aceitas = buscar_ocorrencias_aceitas(current_user_id)

    # Configuração da tabela AgGrid
    grid = ui.aggrid({
        "columnDefs": [
            {"headerName": "Data", "field": "data"},
            {"headerName": "Cliente", "field": "cliente"},
            {"headerName": "Nº Processo", "field": "num_processo"},
            {"headerName": "Responsável", "field": "responsavel"},
            {"headerName": "Status", "field": "status"},
            {"headerName": "Título", "field": "titulo"},
            {
                "headerName": "Conteúdo",
                "field": "conteudo",
                "cellRenderer": "conteudoCellRenderer",
                "onCellClicked": {"function": "handleUserOccurrenceClick"}
            },
        ],
        "rowData": ocorrencias_aceitas or [{
            "id": "",
            "cliente": "Nenhuma ocorrência encontrada",
            "num_processo": "",
            "responsavel": "",
            "data": "",
            "status": "",
            "titulo": "",
            "conteudo": ""
        }],
        "defaultColDef": {
            "resizable": True,
            "sortable": True,
            "filter": True,
            "flex": 1,
            "minWidth": 100,
            "cellClass": "cell-wrap-text",
        },
        "suppressCellSelection": True,
    }).classes("w-full h-[500px] mx-auto").style(
        "background: transparent; border: 5px solid rgba(255, 255, 255, 0.5); overflow-x: auto; max-width: 100%; min-width: 300px;"
    )

    # JavaScript para lidar com os cliques
    ui.add_head_html(f"""
    <script>
        // Função para renderizar o conteúdo 
        function conteudoCellRenderer(params) {{
            const maxLength = 50;
            const content = params.value || '';
            return content.length > maxLength 
                ? content.substring(0, maxLength) + '...' 
                : content;
        }}

        // Handler para clique na célula de conteúdo
        function handleUserOccurrenceClick(event) {{
            if (event.column.colId === 'conteudo') {{
                const rowData = event.data;
                ni.emit('user_occurrence_clicked', rowData)
            }}
        }}
    </script>
    """)

    # Botão de atualizar
    with ui.row().classes("mx-auto gap-x-10"):
        ui.button("Atualizar",
                  on_click=lambda: atualizar_tabela_user(grid, current_user_id)
                  ).style("color: white; font-weight: bold; background-color: #008B8B !important;").classes("btn-secondary w-48")

    # Handler para o evento de clique
    def handle_user_occurrence(data: dict):
        ocorrencia_data = (
            data.get('id'),
            data.get('cliente'),
            data.get('num_processo'),
            data.get('responsavel'),
            data.get('responsavel_id'),
            data.get('data'),
            data.get('status'),
            data.get('titulo'),
            data.get('conteudo'),
            data.get('criador_id')
        )

        detalhes_ocorrencia(ocorrencia_data)

    ui.on('user_occurrence_clicked', handle_user_occurrence)

# ---------------------------------- ATUALIZA A TABELA OCORRENCIAS  -------------------------------

def carregar_ocorrencia():
    global grid  # acessa o grid globalmente

    if grid:
        current_user_id = app.storage.user.get("userid", None)
        novas_ocorrencias = buscar_ocorrencias_aceitas(current_user_id)

        grid.set_data(novas_ocorrencias)  # atualiza a tabela

# --------------------------------------- ATUALIZA A TABELA DO USER -------------------------------------

def atualizar_tabela_user(grid, user_id):
    novas_ocorrencias = buscar_ocorrencias_aceitas(user_id)

    if not novas_ocorrencias:
        novas_ocorrencias = [{
            "id": "",
            "cliente": "Nenhuma ocorrência encontrada",
            "num_processo": "",
            "responsavel": "",
            "data": "",
            "status": "",
            "titulo": "",
            "conteudo": ""
        }]

    grid.options["rowData"] = novas_ocorrencias
    grid.update()




