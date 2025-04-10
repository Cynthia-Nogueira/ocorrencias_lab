from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection
from Programa_NiceGui.paginas.notificacoes_servicos.tabela import aceitar_ocorrencia
from datetime import datetime, date
from nicegui import ui, app

# ----------------------------------- ABRE UMA CAIXA COM DETALHES DA MENSAGEM ------------------------------------


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
            SELECT o.id, o.cliente, o.num_processo, o.data, o.conteudo
            FROM notificacoes n
            JOIN ocorrencias o ON n.ocorrencia_id = o.id
            WHERE n.id = %s AND n.usuario_id = %s
        """

        cursor.execute(query, (notificacao_id, current_user_id))
        resultado = cursor.fetchone()


        if not resultado:
            ui.notify("Erro: Detalhes não encontrados.", type="negative")
            print(
                f"Erro: Nenhuma ocorrência encontrada para notificacao_id={notificacao_id} e usuario_id={current_user_id}")
            return

        #  if not resultado:
       #     ui.notify("Erro: Detalhes não encontrados.", type="negative")
        #    return

        ocorrencia_id, cliente, num_processo, data_ocorrencia, conteudo_ocorrencia, *_ = resultado


        # garante que data_ocorrencia é uma string formatada
        data_formatada = datetime.strptime(str(data_ocorrencia), "%Y-%m-%d").strftime("%d/%m/%Y")


        # Criar o diálogo
        with ui.dialog() as detalhe_dialog:
            with ui.card().style('background-color: #ebebeb !important;').classes("w-96 mx-auto"):
                ui.label("Detalhes da Notificação").classes("text-lg font-bold mx-auto q-mb-sm")

                # Exibir detalhes formatados
                with ui.column():
                    for titulo, valor in [
                        ("Cliente", cliente),
                        ("Nº Processo", num_processo),
                        ("Data", data_formatada),
                    ]:
                        with ui.row():
                            ui.label(f"{titulo}:").classes("font-bold")
                            ui.label(valor)

                    # Justificar o texto de detalhes
                    with ui.row():
                        ui.label("Detalhes:").classes("font-bold")
                    with ui.row():
                        ui.label(conteudo_ocorrencia).classes("text-justify").style("text-align: justify;")

                # Botões centralizados
                with ui.row().classes("w-full flex justify-center items-center q-mt-md gap-4"):
                    ui.button("Fechar", on_click=detalhe_dialog.close
                              ).style("color: white; font-weight: bold; background-color: #008B8B !important;"
                                      ).classes("bg-green-700 text-white font-bold px-4 py-2 w-32 text-center")

                    ui.button("Aceitar",
                              on_click=lambda: mostrar_confirmacao(ocorrencia_id, current_user_id, detalhe_dialog)
                              ).style("color: white; font-weight: bold; background-color: #008B8B !important;"
                                      ).classes("bg-blue-700 text-white font-bold px-4 py-2 w-32 text-center")


        detalhe_dialog.open()

    finally:
        cursor.close()
        conn.close()

# --------------------------------------- CAIXA DE CONFIRMACAO --------------------------------

def mostrar_confirmacao(ocorrencia_id, ultima_usuario_id, detalhe_dialog):
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


