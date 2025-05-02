from os.path import curdir

from docutils.nodes import status

from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection
from Programa_NiceGui.paginas.notificacoes_servicos.notificacao_utils import enviar_notificacao, carregar_notificacoes
from Programa_NiceGui.paginas.notificacoes_servicos.tabela import aceitar_ocorrencia
from datetime import datetime
from nicegui import ui, app

# ----------------------------------- ABRE UMA CAIXA COM DETALHES DA MENSAGEM ------------------------------------

def visualizar_notificacao(notificacao_id, notificacao_elements):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        current_user_id = app.storage.user.get("userid", None)
        if current_user_id is None:
            ui.notify("Erro: Usuário não autenticado.", type="negative")
            return

        # Consulta os detalhes da notificação
        query_detalhes = """
            SELECT o.id, o.cliente, o.num_processo, o.data, o.titulo, o.conteudo, o.responsavel_id, o.status, n.tipo_ocorrencia
            FROM notificacoes n
            JOIN ocorrencias o ON n.ocorrencia_id = o.id
            WHERE n.id = %s AND n.usuario_id = %s
        """
        cursor.execute(query_detalhes, (notificacao_id, current_user_id))
        resultado = cursor.fetchone()

        if not resultado:
            ui.notify("Erro: Detalhes não encontrados.", type="negative")
            print(f"[ERRO] Nenhuma ocorrência encontrada (notificacao_id={notificacao_id}, usuario_id={current_user_id})")
            return

        ocorrencia_id, cliente, num_processo, data_ocorrencia, titulo_ocorrencia, conteudo_ocorrencia, responsavel_id, status_ocorrencia, tipo_ocorrencia  = resultado

        # Formatar data
        if isinstance(data_ocorrencia, str):
            data_ocorrencia = datetime.strptime(data_ocorrencia, "%Y-%m-%d %H:%M:%S")
        data_formatada = data_ocorrencia.strftime("%d/%m/%Y")

        # Atualiza o status da notificação para 'lida' no banco de dados
        query_atualiza = "UPDATE notificacoes SET lida = 1 WHERE id = %s AND usuario_id = %s"
        cursor.execute(query_atualiza, (notificacao_id, current_user_id))
        conn.commit()

        # Recarrega as notificações
        global notificacoes
        notificacoes, _ = carregar_notificacoes(current_user_id)

        # Atualiza o estilo do botão na interface, se ele ainda existir no diálogo
        if notificacao_id in notificacao_elements:
            notificacao_elements[notificacao_id].style("color: #808080 !important; font-weight: normal; background-color: #E5FCF2 !important;")
            notificacao_elements[notificacao_id].update() # Notifica o NiceGUI para re-renderizar

        # Criar o diálogo de detalhes
        with ui.dialog() as detalhe_dialog:
            with ui.card().style('background-color: #ececf5 !important; width: 480px; height: 440px;').classes("mx-auto"):
                ui.label("Detalhes da Notificação").style("font-size: 1.25rem; margin: 0 auto; display: block;").classes("font-bold q-mb-sm")
                with ui.column():
                    for title, valor in [
                        ("Cliente", cliente),
                        ("Nº Processo", num_processo),
                        ("Data", data_formatada),
                        ("Título", titulo_ocorrencia),
                    ]:
                        with ui.row():
                            ui.label(f"{title}:").classes("font-bold")
                            ui.label(valor)
                    with ui.row():
                        ui.label("Detalhes:").classes("font-bold")
                    with ui.row():
                        ui.label(conteudo_ocorrencia).classes("text-justify").style("text-align: justify;")
                with ui.row().classes("w-full flex justify-center items-center q-mt-md gap-4"):
                    print(f"[DEBUG] tipo_ocorrencia: '{tipo_ocorrencia}'")

                    ui.button("Fechar", on_click=detalhe_dialog.close
                              ).style("color: white; font-weight: bold; background-color: #0a0476 !important;"
                                      ).classes("bg-green-700 text-white font-bold px-4 py-2 w-32 text-center")

                    if responsavel_id is None and status_ocorrencia != "Cancelada" and tipo_ocorrencia in ["Devolvida", "Não atribuída", "Expirada"]:
                        ui.button("Aceitar",
                                  on_click=lambda: mostra_confirmacao(ocorrencia_id, current_user_id, detalhe_dialog)
                                  ).style("color: white; font-weight: bold; background-color: #008B8B !important;"
                                          ).classes("bg-blue-700 text-white font-bold px-4 py-2 w-32 text-center")
        detalhe_dialog.open()

    finally:
        cursor.close()
        conn.close()

# --------------------------------------- CAIXA DE CONFIRMACAO --------------------------------

def mostra_confirmacao(ocorrencia_id, ultima_usuario_id, detalhe_dialog):
    with ui.dialog() as confirm_dialog:
        with ui.card().style('background-color: #ebebeb !important;').classes("w-96 mx-auto"):
            ui.label("Tem certeza que deseja aceitar esta ocorrência?").classes(
                "text-lg font-bold mx-auto q-mb-sm text-center")

            with ui.row().classes("w-full flex justify-center items-center q-mt-md gap-4"):
                ui.button("Não", on_click=confirm_dialog.close).style(
                    "color: white; font-weight: bold; background-color: #FF6347 !important;"
                ).classes("text-white font-bold px-4 py-2 w-32 text-center")

                ui.button("Sim", on_click=lambda: aceitar_ocorrencia(ocorrencia_id, ultima_usuario_id,
                      detalhe_dialog, confirm_dialog)).style("color: white; font-weight: bold; background-color: "
                      "#008B8B !important;").classes("text-white font-bold px-4 py-2 w-32 text-center")

        confirm_dialog.open()

# ---------------------------------- NOTIFICA OS USERS DA OCORRENCIA DEVOLVIDA ------------------------

def notifica_ocorrencia_devolvida(ocorrencia_id, nome_usuario):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT cliente, titulo FROM ocorrencias WHERE id = %s", (ocorrencia_id,))
        cliente, titulo = cursor.fetchone()

        mensagem = f"🔄 {nome_usuario} devolveu a ocorrência do Cliente: {cliente} (Título: {titulo})"

        # Pegando users
        cursor.execute("SELECT id FROM utilizador")
        usuarios = cursor.fetchall()

        for (usuario_id,) in usuarios:
            enviar_notificacao(usuario_id, mensagem, ocorrencia_id, tipo_ocorrencia="Devolvida")

    except Exception as e:
        ui.notify(f"Erro ao notificar devolução: {e}", type="negative")
    finally:
        cursor.close()
        conn.close()

# ---------------------------------- NOTIFICA OS USERS DA OCORRENCIA canceladas ------------------------

def notifica_ocorrencia_cancelada(ocorrencia_id, nome_usuario):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT cliente, titulo FROM ocorrencias WHERE id = %s", (ocorrencia_id,))
        cliente, titulo = cursor.fetchone()

        mensagem = f"📛 {nome_usuario} cancelou a ocorrência '{titulo}'"

        # Pegando users
        cursor.execute("SELECT id FROM utilizador")
        usuarios = cursor.fetchall()

        for (usuario_id,) in usuarios:
            enviar_notificacao(usuario_id, mensagem, ocorrencia_id)

    except Exception as e:
        ui.notify(f"Erro ao notificar devolução: {e}", type="negative")
    finally:
        cursor.close()
        conn.close()


# ---------------------------------- NOTIFICA OCORRENCIA CONCLUIDAS ------------------------

def notifica_ocorrencias_concluidas(ocorrencia_id, novo_status, nome_usuario):
    if novo_status != "Concluída":
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Buscar informações da ocorrência
        cursor.execute("SELECT status, criador_id, titulo FROM ocorrencias WHERE id = %s", (ocorrencia_id,))
        resultado = cursor.fetchone()

        if not resultado:
            ui.notify("[ERRO] Ocorrência não encontrada!")
            return

        _, criador_id, titulo = resultado

        mensagem = f"🎯 A ocorrência '{titulo}' foi concluída por {nome_usuario}."

        # Enviar notificação para todos os usuários
        cursor.execute("SELECT id FROM utilizador")
        usuarios = cursor.fetchall()

        for (usuario_id,) in usuarios:
            enviar_notificacao(usuario_id, mensagem, ocorrencia_id, tipo_ocorrencia="Concluída")


    except Exception as e:
        ui.notify(f"[ERRO] Falha ao notificar conclusão da ocorrência: {e}")

    finally:
        cursor.close()
        conn.close()












