from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection
from Programa_NiceGui.paginas.notificacoes_servicos.tabela import aceitar_ocorrencia
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
                   SELECT o.id, 
                   o.cliente,
                   o.num_processo,
                   o.data, o.conteudo
                   FROM notificacoes n
                   JOIN ocorrencias o ON n.ocorrencia_id = o.id
                   WHERE n.id = %s AND n.usuario_id = %s
               """
        cursor.execute(query, (notificacao_id, current_user_id))
        resultado = cursor.fetchone()

        if not resultado:
            ui.notify("Erro: Detalhes não encontrados.", type="negative")
            return

        ocorrencia_id, cliente, num_processo, data_ocorrencia, conteudo_ocorrencia = resultado

        # Criar a caixa de diálogo com os detalhes
        with ui.dialog() as detalhe_dialog:
            with ui.card():
                ui.label(f"📌 Cliente: {cliente}").classes("text-lg font-bold")
                ui.label(f"📁 Nº Processo: {num_processo}")
                ui.label(f"📅 Data: {data_ocorrencia}")
                ui.label(f"📝 Detalhes: {conteudo_ocorrencia}")

                with ui.row():
                    ui.button("Fechar", on_click=detalhe_dialog.close).classes("btn-secondary")
                    ui.button("Aceitar", on_click=lambda: aceitar_ocorrencia(ocorrencia_id, current_user_id,
                                                                             detalhe_dialog)).classes("btn-primary")

            detalhe_dialog.open()

    finally:
        cursor.close()
        conn.close()


def fechar_notificacao(detalhe_dialog):
    detalhe_dialog.close()


