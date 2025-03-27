from nicegui import ui, app
from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection
from Programa_NiceGui.paginas.notificacoes_servicos.notificacoes import visualizar_notificacao

# ------------------------------------------- LISTA AS NOTIFICACOES --------------------------------------

def carregar_notificacoes(usuario_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "SELECT id, mensagem, data_notificacao, lida, ocorrencia_id FROM notificacoes WHERE usuario_id = %s ORDER BY data_notificacao DESC"
        cursor.execute(query, (usuario_id,))
        notificacoes_db = cursor.fetchall()

        dados_tabela = []
        notificacoes_nao_lidas = 0

        for notificacao in notificacoes_db:
            id, mensagem, data_notificacao, lida, ocorrencia_id = notificacao
            if not lida:
                notificacoes_nao_lidas += 1
            dados_tabela.append({
                "id": id,
                "mensagem": mensagem,
                "data_notificacao": data_notificacao,
                "lida": lida,
                "ocorrencia_id": ocorrencia_id
            })

        return dados_tabela, notificacoes_nao_lidas  # Retorna notificações e contador de não lidas

    finally:
        cursor.close()
        conn.close()

# --------------------------------- EXIBE AS NOTIFICACOES NO MENU ---------------------------

def exibir_notificacoes_menu():
    global notificacoes
    current_user_id = app.storage.user.get("userid", None)

    if current_user_id:
        notificacoes, _ = carregar_notificacoes(current_user_id)

    with ui.dialog() as dialog:
        with ui.card().classes("w-120 mx-auto q-pa-md") as card_notificacoes:
            ui.label("Notificações:").style("color: #40403e; font-weight: bold;").classes(
                "text-2xl mx-auto font-bold mb-4")

            card_notificacoes.classes("q-pa-md")
            card_notificacoes.style(
                "background-color: #d2e9dd; border-radius: 10px; overflow-y: auto;"
                "width: 600px; height: 500px;"
            )

            with ui.column().classes("w-full"):
                for notificacao in notificacoes:
                    notificacao_id = notificacao["id"]
                    mensagem = notificacao["mensagem"]

                    if not notificacao["lida"]:
                        ui.button(
                            mensagem,
                            on_click=lambda id=notificacao_id: visualizar_notificacao(id)
                        ).style("color: white; font-weight: bold; background-color: #B6C9BF !important;") \
                            .classes("q-pa-sm text-left full-width")
                    else:
                        ui.label(mensagem).classes("q-pa-sm text-gray-500") \
                            .style("background-color: #d2e9dd !important; border-radius: 8px; padding: 8px;")

            ui.button("Fechar", on_click=dialog.close).style(
                "color: white; font-weight: bold; background-color: #5a7c71 !important;"
            ).classes("mx-auto q-mt-md")

        dialog.open()


# ---------------------------------- FILTRA AS OCORRENCIAS: CONCLUIDAS --------------------------------

def ocorrencia_concluida():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Criação do dialog para exibir as ocorrências
    with ui.dialog() as dialog:
        with ui.card().classes("w-120 mx-auto q-pa-md") as card_notificacoes:
            ui.label("Ocorrências concluídas").style("color: #40403e; font-weight: bold;").classes(
                "text-2xl mx-auto font-bold mb-4")

            card_notificacoes.classes("q-pa-md")
            card_notificacoes.style(
                "background-color: #d2e9dd; border-radius: 10px; overflow-y: auto; width: 600px; height: 500px;"
            )

            with ui.column().classes("w-full") as column_notificacoes:

                # Busca as ocorrências concluídas
                try:
                    query = """SELECT id, cliente, num_processo, responsavel, data, status, conteudo 
                                  FROM ocorrencias 
                                  WHERE status = "Concluída";"""
                    cursor.execute(query)
                    ocorrencias = cursor.fetchall()

                    if not ocorrencias:
                        ui.notify("Nenhuma ocorrência concluída encontrada.", type="negative")
                        return

                    # Adiciona as ocorrências no dialog após a pesquisa
                    for ocorrencia in ocorrencias:
                        ocorrencia_id, cliente, num_processo, responsavel, data_ocorrencia, status, conteudo = ocorrencia

                        # Exibe a notificação ou botão para ver mais
                        # detalhes
                        ui.button(
                            f"{cliente} - {num_processo} - {responsavel}",
                            on_click=lambda id=ocorrencia_id: visualizar_notificacao(id)
                        ).style("color: white; font-weight: bold; background-color: #B6C9BF !important;") \
                            .classes("q-pa-sm text-left full-width")

                finally:
                    cursor.close()
                    conn.close()

            ui.button("Fechar", on_click=dialog.close).style(
                "color: white; font-weight: bold; background-color: #5a7c71 !important;"
            ).classes("mx-auto q-mt-md")


    # Abre o dialog com os dados
    dialog.open()


# ---------------------------------- FILTRA AS OCORRENCIAS: E EXECUCAO  --------------------------------


def ocorrencia_execucao():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Criação do dialog para exibir as ocorrências
    with ui.dialog() as dialog:
        with ui.card().classes("w-120 mx-auto q-pa-md") as card_notificacoes:
            ui.label("Ocorrências em execução").style("color: #40403e; font-weight: bold;").classes(
                "text-2xl mx-auto font-bold mb-4")

            card_notificacoes.classes("q-pa-md")
            card_notificacoes.style(
                "background-color: #d2e9dd; border-radius: 10px; overflow-y: auto; width: 600px; height: 500px;"
            )

            with ui.column().classes("w-full") as column_notificacoes:

                # Busca as ocorrências concluídas
                try:
                    query = """SELECT id, cliente, num_processo, responsavel, data, status, conteudo 
                                      FROM ocorrencias 
                                      WHERE status = "Em Execução";"""
                    cursor.execute(query)
                    ocorrencias = cursor.fetchall()

                    if not ocorrencias:
                        ui.notify("Nenhuma ocorrência em execução encontrada.", type="negative")
                        return

                    # Adiciona as ocorrências no dialog após a pesquisa
                    for ocorrencia in ocorrencias:
                        ocorrencia_id, cliente, num_processo, responsavel, data_ocorrencia, status, conteudo = ocorrencia

                        # Exibe a notificação ou botão para ver mais
                        # detalhes
                        ui.button(
                            f"{cliente} - {num_processo} - {responsavel}",
                            on_click=lambda id=ocorrencia_id: visualizar_notificacao(id)
                        ).style("color: white; font-weight: bold; background-color: #B6C9BF !important;") \
                            .classes("q-pa-sm text-left full-width")

                finally:
                    cursor.close()
                    conn.close()

            ui.button("Fechar", on_click=dialog.close).style(
                "color: white; font-weight: bold; background-color: #5a7c71 !important;"
            ).classes("mx-auto q-mt-md")

    # Abre o dialog com os dados
    dialog.open()

# ---------------------------------- FILTRA AS OCORRENCIAS: EM ESPERA --------------------------------


def ocorrencia_espera():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Criação do dialog para exibir as ocorrências
    with ui.dialog() as dialog:
        with ui.card().classes("w-120 mx-auto q-pa-md") as card_notificacoes:
            ui.label("Ocorrências em espera").style("color: #40403e; font-weight: bold;").classes(
                "text-2xl mx-auto font-bold mb-4")

            card_notificacoes.classes("q-pa-md")
            card_notificacoes.style(
                "background-color: #d2e9dd; border-radius: 10px; overflow-y: auto; width: 600px; height: 500px;"
            )

            with ui.column().classes("w-full") as column_notificacoes:

                # Busca as ocorrências concluídas
                try:
                    query = """SELECT id, cliente, num_processo, responsavel, data, status, conteudo 
                                      FROM ocorrencias 
                                      WHERE status = "Em Espera";"""
                    cursor.execute(query)
                    ocorrencias = cursor.fetchall()

                    if not ocorrencias:
                        ui.notify("Nenhuma ocorrência em espera encontrada.", type="negative")
                        return

                    # Adiciona as ocorrências no dialog após a pesquisa
                    for ocorrencia in ocorrencias:
                        ocorrencia_id, cliente, num_processo, responsavel, data_ocorrencia, status, conteudo = ocorrencia

                        # Exibe a notificação ou botão para ver mais
                        # detalhes
                        ui.button(
                            f"{cliente} - {num_processo} - {responsavel}",
                            on_click=lambda id=ocorrencia_id: visualizar_notificacao(id)
                        ).style("color: white; font-weight: bold; background-color: #B6C9BF !important;") \
                            .classes("q-pa-sm text-left full-width")

                finally:
                    cursor.close()
                    conn.close()

            ui.button("Fechar", on_click=dialog.close).style(
                "color: white; font-weight: bold; background-color: #5a7c71 !important;"
            ).classes("mx-auto q-mt-md")

    # Abre o dialog com os dados
    dialog.open()

# ---------------------------------- FILTRA AS OCORRENCIAS: NAO ATRIBUIDAS --------------------------------

def nao_atribuida():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Criação do dialog para exibir as ocorrências
    with ui.dialog() as dialog:
        with ui.card().classes("w-120 mx-auto q-pa-md") as card_notificacoes:
            ui.label("Ocorrências não atribuídas").style("color: #40403e; font-weight: bold;").classes(
                "text-2xl mx-auto font-bold mb-4")

            card_notificacoes.classes("q-pa-md")
            card_notificacoes.style(
                "background-color: #d2e9dd; border-radius: 10px; overflow-y: auto; width: 600px; height: 500px;"
            )

            with ui.column().classes("w-full") as column_notificacoes:

                # Busca as ocorrências concluídas
                try:
                    query = """SELECT id, cliente, num_processo, responsavel, data, status, conteudo 
                                          FROM ocorrencias 
                                          WHERE responsavel = NULL;"""

                    cursor.execute(query)
                    ocorrencias = cursor.fetchall()

                    if not ocorrencias:
                        ui.notify("Todas as ocorrênicas estão atribuídas.", type="negative")
                        return

                    # Adiciona as ocorrências no dialog após a pesquisa
                    for ocorrencia in ocorrencias:
                        ocorrencia_id, cliente, num_processo, responsavel, data_ocorrencia, status, conteudo = ocorrencia

                        # Exibe a notificação ou botão para ver mais
                        # detalhes
                        ui.button(
                            f"{cliente} - {num_processo} - {responsavel}",
                            on_click=lambda id=ocorrencia_id: visualizar_notificacao(id)
                        ).style("color: white; font-weight: bold; background-color: #B6C9BF !important;") \
                            .classes("q-pa-sm text-left full-width")

                finally:
                    cursor.close()
                    conn.close()

            ui.button("Fechar", on_click=dialog.close).style(
                "color: white; font-weight: bold; background-color: #5a7c71 !important;"
            ).classes("mx-auto q-mt-md")

    # Abre o dialog com os dados
    dialog.open()