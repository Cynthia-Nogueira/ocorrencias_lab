from nicegui import ui, app
from datetime import datetime
from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection
from Programa_NiceGui.paginas.notificacoes_servicos.notificacao_utils import carregar_notificacoes
from Programa_NiceGui.paginas.notificacoes_servicos.notificacoes import visualizar_notificacao, mostra_confirmacao
from Programa_NiceGui.paginas.notificacoes_servicos.ocorrencias_utils import atualiza_status, confirmar_alteracao_status

# --------------------------------- EXIBE AS NOTIFICACOES NO MENU ---------------------------

def exibir_notificacoes_menu():
    global notificacoes
    current_user_id = app.storage.user.get("userid", None)

    if current_user_id:
        notificacoes, _ = carregar_notificacoes(current_user_id)

    with ui.dialog() as dialog:
        with ui.card().classes("w-120 mx-auto").style("padding: 8px 0;") as card_notificacoes:
            card_notificacoes.style("background-color: #008B8B; border-radius: 10px; overflow-y: auto; width: 600px; height: 600px;")


            # Título fixo no topo
            with ui.row().classes("w-full justify-center items-center q-pa-sm").style("position: sticky; top: 0; background-color: #008B8B; z-index: 1;"):
                ui.label("Notificações").style("background-color: #008B8B; color: #fff8ff !important;").classes("text-2xl font-bold text-center")

            # Área scrollável com notificações
            with ui.scroll_area().style("flex-grow: 1; overflow-y: auto; background-color: #ececf5;").classes("w-full q-px-md q-pt-sm"):

                with ui.column().classes("w-full gap-2"):
                    for notificacao in notificacoes:
                        notificacao_id = notificacao["id"]
                        mensagem = notificacao["mensagem"]


                        #ISSO MUDA A COR????

                        if not notificacao["lida"]:
                            ui.button(
                                mensagem,
                                on_click=lambda id=notificacao_id: visualizar_notificacao(id)
                            ).style("color: #464646 !important; font-weight: bold; background-color: #D2E9DD !important;"
                            ).classes("q-pa-sm text-left full-width")
                        else:
                            ui.label(mensagem).style("background-color: #008B8B  !important; border-radius: 8px; padding: 8px;"
                                                     ).classes("q-pa-sm text-left text-gray-500 full-width")


            # Botão fechar fixo no rodapé
            with ui.row().style("position: sticky; bottom: 0; background-color: #008B8B; z-index: 1;").classes("w-full justify-center q-pa-sm"):

                ui.button("Fechar", on_click=dialog.close).style(
                    "color: black !important; font-weight: bold; background-color: #fff8ff !important;"
                ).classes("text-white font-bold px-4 py-2")

        dialog.open()

# ----------------------------------- FILTRA AS OCORRENCIAS POR STATUS -------------------------------------

def ocorrencias_filtradas(status: str, titulo: str, condicao_extra: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    with ui.dialog() as dialog:
        with ui.card().classes("w-120 mx-auto").style("padding: 8px 0;") as card_notificacoes:
            card_notificacoes.style("background-color: #008B8B; border-radius: 10px; overflow-y: auto; width: 600px; height: 600px;")

            # Título fixo no topo
            with ui.row().classes("w-full justify-center items-center q-pa-sm").style("position: sticky; top: 0; background-color: #008B8B; z-index: 1;"):
                ui.label(titulo).style("background-color: #008B8B; color: #fff8ff !important; padding: 8px 0 4px 0").classes("text-center font-bold text-2xl")

            # Scroll Area para as notificações
            with ui.column().classes("w-full") as column_notificacoes:
                with ui.scroll_area().style("flex-grow: 1; overflow-y: auto; background-color: #ececf5;").classes("w-full q-px-md q-pt-sm"):
                    try:
                        if condicao_extra:
                            query = f"""
                                SELECT id, cliente, num_processo, responsavel, responsavel_id, data, status, titulo, conteudo 
                                FROM ocorrencias 
                                WHERE {condicao_extra}
                                ORDER BY data DESC;
                            """
                            params = ()

                        else:
                            if status == "Em Espera":
                                query = """
                                    SELECT id, cliente, num_processo, responsavel, responsavel_id, data, status, titulo, conteudo 
                                    FROM ocorrencias 
                                    WHERE responsavel IS NOT NULL AND status = 'Em Espera'
                                    ORDER BY data DESC;
                                """
                                params = ()

                            elif status == "Não Atribuída":
                                query = """
                                    SELECT id, cliente, num_processo, responsavel, responsavel_id, data, status, titulo, conteudo 
                                    FROM ocorrencias 
                                    WHERE responsavel IS NULL AND status = 'Não atribuída'
                                    ORDER BY data DESC;
                                """
                                params = ()

                            elif status is None:
                                query = """
                                    SELECT id, cliente, num_processo, responsavel, responsavel_id, data, status, titulo, conteudo 
                                    FROM ocorrencias 
                                    WHERE status IS NULL
                                    ORDER BY data DESC;
                                """
                                params = ()

                            else:
                                query = """
                                    SELECT id, cliente, num_processo, responsavel, responsavel_id, data, status, titulo, conteudo 
                                    FROM ocorrencias 
                                    WHERE status = %s
                                    ORDER BY data DESC;
                                """
                                params = (status,)

                        cursor.execute(query, params)
                        ocorrencias = cursor.fetchall()

                        if not ocorrencias:
                            ui.notify(f"Nenhum resultado encontrado para '{titulo}'.", type="negative")
                            return

                        for ocorrencia in ocorrencias:
                            ui.button(
                                f"{ocorrencia[3] or 'Não Atribuído'}: Cliente  {ocorrencia[1]} - Título:  '{ocorrencia[7]}'",
                                on_click=lambda o=ocorrencia: detalhes_ocorrencia(o)).style("color: #464646 !important; font-weight: bold; background-color: #D2E9DD !important;"
                                                                                            ).classes("q-pa-sm text-left full-width")

                    finally:
                        cursor.close()
                        conn.close()

                # Botão de Fechar no rodapé
                with ui.row().style("position: sticky; bottom: 0; background-color: #008B8B; z-index: 1; padding: 4px 0 8px 0;").classes(
                                                                                                                "w-full justify-center"):
                    ui.button("Fechar", on_click=dialog.close).style(
                        "color: black !important; font-weight: bold; background-color: #fff8ff !important;"
                    ).classes("text-white font-bold px-4 py-2")

            dialog.open()

# ------------------------------------------------- CHAMA O DETALHE DAS OCORRENCIAS ------------------------------------------------

def detalhes_ocorrencia(ocorrencia):
    ocorrencia_id, cliente, num_processo, responsavel, responsavel_id, data_ocorrencia, status, titulo, conteudo_ocorrencia = ocorrencia
    #current_user_id = app.storage.user.get("userid")
    current_user_id = int(app.storage.user.get("userid"))
    responsavel_id = int(responsavel_id) if responsavel_id is not None else None

    detalhe_dialog = ui.dialog()

    with detalhe_dialog:
        with ui.card().style('background-color: #ebebeb !important; width: 480px; height: 440px;').classes("mx-auto"):

            ui.label("Detalhes da Ocorrência").style("font-size: 1.25rem; margin: 0 auto; display: block;").classes(
                "font-bold q-mb-sm")

            print("Responsável ID:", responsavel_id)
            print("User logado ID:", current_user_id)
            print("Status atual:", status)


            # --- SELECT de status (só se o user for o responsável) ---
            if responsavel_id == current_user_id and status in ["Em execução", "Em espera"]:
                with ui.row().classes("items-center q-mb-md"):
                    ui.label("Atualizar Status:").classes("font-bold")
                    status_selecionado = ui.select(
                        options=["", "Em Execução", "Em Espera", "Devolvida", "Concluída", "Cancelada"],
                        value=""
                    ).style("background-color: white; min-width: 200px;").props("outlined dense")

            # Área com rolagem para os dados da ocorrência (corrigido duplicação de with)
            with ui.column().style(
                "max-height: 300px; overflow-y: auto; overflow-x: hidden; padding-right: 8px; width: 100%; box-sizing: border-box;"
            ).classes("q-mb-sm"):

                if isinstance(data_ocorrencia, str):
                    data_ocorrencia = datetime.strptime(data_ocorrencia, "%Y-%m-%d %H:%M:%S")
                data_formatada = data_ocorrencia.strftime('%d-%m-%y')

                for titulo_info, valor in [
                    ("Cliente", cliente),
                    ("Nº Processo", num_processo),
                    ("Data", data_formatada),
                    ("Título", titulo),
                ]:
                    with ui.row():
                        ui.label(f"{titulo_info}:").classes("font-bold")
                        ui.label(valor)

                with ui.row():
                    ui.label("Detalhes:").classes("font-bold")
                with ui.row():
                    ui.label(conteudo_ocorrencia).style("text-align: justify; white-space: pre-wrap; width: 100%;").classes("text-base")

            # Botões de ação
            with ui.row().classes("w-full flex justify-center items-center q-mt-md gap-4"):
                ui.button("Fechar", on_click=detalhe_dialog.close).style(
                    "color: white; font-weight: bold; background-color: #008B8B !important;"
                ).classes("bg-green-700 text-white font-bold px-4 py-2 w-32 text-center")

                if responsavel_id == current_user_id and status in ["Em execução", "Em espera"]:
                    ui.button(
                        "Confirmar",
                        on_click=lambda: (
                            confirmar_alteracao_status(ocorrencia_id, status_selecionado.value, detalhe_dialog)
                            if status_selecionado.value else ui.notify(
                                "Por favor, selecione um status válido!", type="warning")
                        )
                    ).style(
                        "color: white; font-weight: bold; background-color: #008B8B !important;"
                    ).classes("bg-green-700 text-white font-bold px-4 py-2 w-32 text-center")

                elif (status == "Devolvida" or responsavel is None) and responsavel_id is None:
                    if current_user_id:
                        ui.button(
                            "Aceitar",
                            on_click=lambda o_id=ocorrencia_id, u_id=current_user_id:
                            mostra_confirmacao(o_id, u_id, detalhe_dialog)
                        ).style(
                            "color: white; font-weight: bold; background-color: #008B8B !important;"
                        ).classes("bg-blue-700 text-white font-bold px-4 py-2 w-32 text-center")

    detalhe_dialog.open()


# ---------------------------- Funções específicas chamando a função genérica -------------------------------------

def ocorrencia_concluida():
    ocorrencias_filtradas("Concluída", "Ocorrências concluídas")

def ocorrencia_execucao():
    ocorrencias_filtradas("Em Execução", "Ocorrências em execução")

def ocorrencia_espera():
    ocorrencias_filtradas("Em Espera", "Ocorrências em espera")

def ocorrencia_devolvida():
    ocorrencias_filtradas("Devolvida", "Ocorrências devolvidas")

def nao_atribuida():
    ocorrencias_filtradas("", "Ocorrências não atribuídas", "responsavel IS NULL")

