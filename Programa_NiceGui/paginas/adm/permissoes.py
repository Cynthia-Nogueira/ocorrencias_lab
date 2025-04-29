from nicegui import ui, app
from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection
from Programa_NiceGui.paginas.notificacoes_servicos.notificacao_utils import enviar_notificacao
from Programa_NiceGui.paginas.notificacoes_servicos.utilizadores import obter_lista_user


# -------------------------------- xxxxxxxxxxxxxxxxxxxx ----------------------------------------

def atribui_ocorrencias(ocorrencia):
    pass



# ----------------------------------------- CONFIRMA A ESCOLHA DO USER --------------------------------------------

def confirma_atribuicao(ocorrencia_id, user_id, admin_id, atribuir_ocorrencia_dialog):
    atribui_ocorrencias(ocorrencia_id, user_id, admin_id)
    ui.notify("✅ Ocorrência atribuída com sucesso!", type="positive")
    atribuir_ocorrencia_dialog.close()









# ---------------------------------- CONFIRMA A RESTAURACAO OCORRENCIA ----------------------------------------

def confirmar_restauracao(ocorrencia_id, dialog):
    with ui.dialog() as confirm_dialog:
        with ui.card().style('background-color: #ebebeb !important;').classes("w-96 mx-auto"):

            ui.label("Deseja realmente restaurar esta ocorrência para 'Não atribuída'?").classes("text-lg font-bold").classes(
                "text-lg font-bold mx-auto q-mb-sm text-center")

            with ui.row().classes("w-full flex justify-center items-center q-mt-md gap-4"):
                ui.button("Não", on_click=confirm_dialog.close).style(
                    "color: white; font-weight: bold; background-color: #FF6347 !important;"
                    ).classes("text-white font-bold px-4 py-2 w-32 text-center")

                ui.button("Sim", on_click=lambda: restaurar_ocorrencia(ocorrencia_id, confirm_dialog, dialog)
                          ).style("color: white; font-weight: bold; background-color: #008B8B !important;").classes(
                          "text-white font-bold px-4 py-2 w-32 text-center")


        confirm_dialog.open()

# ---------------------------------- RESTAURA A OCORRENCIA ----------------------------------------

def restaurar_ocorrencia(ocorrencia_id, confirm_dialog, detalhe_dialog):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Primeiro, busca o título da ocorrência
        cursor.execute("SELECT titulo FROM ocorrencias WHERE id = %s", (ocorrencia_id,))
        resultado = cursor.fetchone()

        if not resultado:
            ui.notify("Título da ocorrência não encontrado.", type="negative")
            return

        titulo = resultado[0]

        #atualiza status da ocorrencia
        cursor.execute("""
            UPDATE ocorrencias
            SET status = 'Não atribuída', responsavel = NULL, responsavel_id = NULL, data_status_alterado = NOW()
            WHERE id = %s
            ORDER BY data_status_alterado DESC, data DESC;
        """, (ocorrencia_id,))
        conn.commit()

        ui.notify("Ocorrência restaurada com sucesso!", type="positive")
        confirm_dialog.close()
        detalhe_dialog.close()

        # Envia notificação para todos os usuários (menos o logado)
        current_user_id = app.storage.user.get("userid")
        nome_user = app.storage.user.get("username") or "Desconhecido"

        mensagem = f"♻️ A ocorrência '{titulo}' foi restaurada por: {nome_user}"

        lista_user = obter_lista_user()

        for user in lista_user:
            if user['id'] != current_user_id:
                enviar_notificacao(user['id'], mensagem, ocorrencia_id, tipo_ocorrencia="Não atribuída")

    except Exception as e:
        ui.notify(f"Erro ao restaurar: {str(e)}", type="negative")
    finally:
        cursor.close()
        conn.close()
