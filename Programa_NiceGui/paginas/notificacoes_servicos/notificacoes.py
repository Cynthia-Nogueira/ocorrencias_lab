from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection
from Programa_NiceGui.paginas.notificacoes_servicos.tabela import aceitar_ocorrencia
from datetime import datetime
from nicegui import ui, app

# ----------------------------------- ABRE UMA CAIXA COM DETALHES DA MENSAGEM ------------------------------------

from datetime import datetime

def visualizar_notificacao(notificacao_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        current_user_id = app.storage.user.get("userid", None)
        if current_user_id is None:
            ui.notify("Erro: Usuário não autenticado.", type="negative")
            return

        # Consulta os detalhes da notificação
        query = """
            SELECT o.id, o.cliente, o.num_processo, o.data, o.titulo, o.conteudo, o.responsavel_id
            FROM notificacoes n
            JOIN ocorrencias o ON n.ocorrencia_id = o.id
            WHERE n.id = %s AND n.usuario_id = %s
        """

        cursor.execute(query, (notificacao_id, current_user_id))
        resultado = cursor.fetchone()

        if not resultado:
            ui.notify("Erro: Detalhes não encontrados.", type="negative")
            print(f"[ERRO] Nenhuma ocorrência encontrada (notificacao_id={notificacao_id}, usuario_id={current_user_id})")
            return

        # Desempacota os dados retornados
        ocorrencia_id, cliente, num_processo, data_ocorrencia, titulo_ocorrencia, conteudo_ocorrencia, responsavel_id = resultado

        # Formatar data (assume datetime, senão faz parse de string)
        if isinstance(data_ocorrencia, str):
            data_ocorrencia = datetime.strptime(data_ocorrencia, "%Y-%m-%d %H:%M:%S")
        data_formatada = data_ocorrencia.strftime("%d/%m/%Y")

        # Criar o diálogo
        with ui.dialog() as detalhe_dialog:
            with ui.card().style('background-color: #ebebeb !important;').classes("w-96 mx-auto"):
                ui.label("Detalhes da Notificação").classes("text-lg font-bold mx-auto q-mb-sm")

                with ui.column():
                    for title, valor in [
                        ("Cliente", cliente),
                        ("Nº Processo", num_processo),
                        ("Data", data_formatada),
                        ("Título", titulo_ocorrencia),  # Corrigido aqui!
                    ]:
                        with ui.row():
                            ui.label(f"{title}:").classes("font-bold")
                            ui.label(valor)

                    # Justificar o texto
                    with ui.row():
                        ui.label("Detalhes:").classes("font-bold")
                    with ui.row():
                        ui.label(conteudo_ocorrencia).classes("text-justify").style("text-align: justify;")

                # Botões centralizados
                with ui.row().classes("w-full flex justify-center items-center q-mt-md gap-4"):
                    ui.button("Fechar", on_click=detalhe_dialog.close
                              ).style("color: white; font-weight: bold; background-color: #008B8B !important;"
                                      ).classes("bg-green-700 text-white font-bold px-4 py-2 w-32 text-center")

                    # Só mostra botão "Aceitar" se a ocorrência ainda não tiver responsável
                    if responsavel_id is None:
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


