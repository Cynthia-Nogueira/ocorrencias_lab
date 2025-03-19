from Programa_NiceGui.paginas.db_conection import get_db_connection, obter_user_logado
from nicegui import ui, app

# ----------------------------------- ABRE UMA CAIXA COM DETALHES DA MENSAGEM ------------------------------------


def mostrar_detalhes_notificacao(mensagem, detalhes, nome_user):
    # Exibe a notificação detalhada em um diálogo
    with ui.dialog() as detalhe_dialog:
        with ui.card().classes("w-96 mx-auto"):
            ui.label("Detalhes da Notificação").classes("text-lg font-bold mx-auto q-mb-sm")

            # Estrutura do texto
            with ui.column():
                partes_mensagem = mensagem.split("\n")
                for linha in partes_mensagem:
                    if ":" in linha:
                        titulo, conteudo = linha.split(":", 1)  # Separa o texto antes e depois dos dois pontos
                        with ui.row():
                            ui.label(titulo + ":").classes("font-bold")
                            ui.label(conteudo.strip())
                    # elif linha.strip() == nome_user:
                    #   ui.label(linha).classes("mx-auto")
                    else:
                        ui.label(linha)

                if detalhes:
                    ui.separator()  # Linha separadora
                    with ui.column():
                        ui.label("Informações Detalhadas").classes("text-md font-semibold q-mb-sm")
                        partes_detalhes = detalhes.split("\n")
                        for linha in partes_detalhes:
                            if ":" in linha:
                                titulo, conteudo = linha.split(":", 1)
                                with ui.row():
                                    ui.label(titulo + ":").classes("font-bold")
                                    ui.label(conteudo.strip())
                            else:
                                ui.label(linha)

            ui.button("Fechar", on_click=detalhe_dialog.close).style(
                "color: white; font-weight: bold; background-color: #5a7c71 !important;"
            ).classes("mx-auto q-mt-md")

    detalhe_dialog.open()

# --------------------------------- EXIBE AS NOTIFICACOES ---------------------------

notificacoes = []   #nao funciona

def mostrar_detalhes_notificacao(detalhes):
    with ui.dialog() as detalhe_dialog, ui.card().classes("w-96 mx-auto"):
        ui.label("Detalhes da Notificação").classes("text-lg font-bold mx-auto q-mb-sm")

        with ui.column():
            partes_detalhes = detalhes.split("\n")
            for linha in partes_detalhes:
                if ":" in linha:
                    titulo, conteudo = linha.split(":", 1)
                    with ui.row():
                        ui.label(titulo + ":").classes("font-bold")
                        ui.label(conteudo.strip())
                else:
                    ui.label(linha)

        ui.button("Fechar", on_click=detalhe_dialog.close).style(
            "color: white; font-weight: bold; background-color: #5a7c71 !important;"
        ).classes("mx-auto q-mt-md")

    detalhe_dialog.open()



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


# -------------------------------- MARCA COMO LIDAS E ATUALIZA NO BD AS NOTIFICACOES --------------------------

#Marca uma notificação como lida, exibe seus detalhes e (opcionalmente) recarrega a lista.


def visualizar_notificacao(notificacao_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        current_user_id = app.storage.user.get("userid", None)

        if current_user_id is None:
            ui.notify("Erro: Usuário não autenticado.", type="negative")
            return

        query = """
            SELECT 
                o.cliente,
                o.num_processo,
                o.data AS data_ocorrencia,
                o.conteudo AS conteudo_ocorrencia
            FROM notificacoes n
            JOIN detalhes_ocorrencias d ON n.id = d.notificacao_id
            JOIN ocorrencias o ON d.ocorrencia_id = o.id
            WHERE n.id = %s AND n.usuario_id = %s
        """
        cursor.execute(query, (notificacao_id, current_user_id))
        resultado = cursor.fetchone()

        if resultado:
            cliente, num_processo, data_ocorrencia, conteudo_ocorrencia = resultado
            detalhes = (
                f"• Nome do cliente: {cliente}\n"
                f"• Nº Processo: {num_processo}\n"
                f"• Data: {data_ocorrencia}\n"
                f"• Conteúdo da Ocorrência: {conteudo_ocorrencia}\n"
            )
        else:
            detalhes = "Detalhes não encontrados para esta notificação."

        # Exibir a caixa de diálogo com os detalhes
        mostrar_detalhes_notificacao(detalhes)

    except Exception as e:
        ui.notify(f"Erro ao carregar notificação: {str(e)}", type="negative")

    finally:
        cursor.close()
        conn.close()


def fechar_notificacao(detalhe_dialog):
    detalhe_dialog.close()

# -------------------------------- ATUALIZA INTERFACE NOTIFICACOES --------------------------


def atualiza_int_notficacoes():
    global notificacoes
    with ui.column().classes("w-full"):
        for notificacao in notificacoes:
            if not notificacao["lida"]:
                ui.button(
                    notificacao["mensagem"],
                    on_click=lambda id=notificacao["id"]: visualizar_notificacao(id)).style("color: gray; font-weight: "
                                    "bold; background-color: #D7EDE1 !important;").classes("q-pa-sm text-left full-width")
            else:
                ui.label(f"{notificacao['mensagem']}").classes("q-pa-sm text-gray-500").style("background-color: #d2e9dd "
                                                                   "!important; border-radius: 8px; padding: 8px;")


# ---------------------------------- ADICIONA UMA NOCA NOTIFICACAO AO DICIONARIO -------------------------------

def add_notificacao(usuario_id, mensagem):
    enviar_notificacao(usuario_id, mensagem)  # Insere no banco
    notificacoes.append({
        "id": len(notificacoes) + 1,  # Pode ser ajustado para pegar do banco
        "mensagem": mensagem,
        "data_notificacao": None,  # Pode ser ajustada para a data atual com datetime.
        "lida": False
    })


# ------------------------------------------- ENVIA AS NOTIFICACOES --------------------------------------

def enviar_notificacao(usuario_id, mensagem):
    conn = get_db_connection()
    if conn is None:
        ui.notify("Erro ao conectar ao banco de dados.", type="negative")
        return

    cursor = conn.cursor()
    try:
        query = "INSERT INTO notificacoes (usuario_id, mensagem, data_notificacao) VALUES (%s, %s, NOW())"
        cursor.execute(query, (usuario_id, mensagem))
        conn.commit()

    except Exception as e:
        ui.notify(f"Erro ao enviar notificação: {str(e)}", type="negative")

    finally:
        cursor.close()
        conn.close()


# ------------------------------------------- LISTA COMPLETA DE NOTIFICACOES --------------------------------------


def carregar_notificacoes(usuario_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "SELECT id, mensagem, data_notificacao, lida FROM notificacoes WHERE usuario_id = %s ORDER BY data_notificacao DESC"
        cursor.execute(query, (usuario_id,))
        notificacoes_db = cursor.fetchall()

        dados_tabela = []
        notificacoes_nao_lidas = 0

        for notificacao in notificacoes_db:
            id, mensagem, data_notificacao, lida = notificacao
            if not lida:
                notificacoes_nao_lidas += 1
            dados_tabela.append({
                "id": id,
                "mensagem": mensagem,
                "data_notificacao": data_notificacao,
                "lida": lida
            })

        return dados_tabela, notificacoes_nao_lidas  # Retorna notificações e contador de não lidas

    finally:
        cursor.close()
        conn.close()



