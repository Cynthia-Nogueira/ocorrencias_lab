from nicegui import ui, app
from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection
from Programa_NiceGui.paginas.notificacoes_servicos.notificacao_utils import enviar_notificacao
from Programa_NiceGui.paginas.notificacoes_servicos.utilizadores import obter_lista_user, utilizador_ativo


# ----------------------------------------- CONFIRMA A ESCOLHA DO USER --------------------------------------------

def confirma_atribuicao(ocorrencia_id, user_id, detalhe_dialog):
    if not user_id:
        ui.notify("Por favor, selecione um responsável!", type="warning")
        return

    # Conectar ao banco de dados para pegar o nome do responsável
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT CONCAT(nome, ' ', apelido) FROM utilizador WHERE id = %s", (user_id,))
    user_name = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    # Exibir o diálogo de confirmação
    with ui.dialog() as confirm_dialog:
        with ui.card().style('background-color: #ebebeb !important;').classes("w-96 mx-auto"):
            ui.label(f"Deseja atribuir essa ocorrência a {user_name}?").classes("text-lg font-bold text-center q-mb-sm")

            with ui.row().classes("w-full flex justify-center items-center q-mt-md gap-4"):
                ui.button("Não", on_click=confirm_dialog.close).style(
                    "color: white; font-weight: bold; background-color: #FF6347 !important;"
                ).classes("text-white font-bold px-4 py-2 w-32 text-center")

                ui.button("Sim", on_click=lambda: salvar_atribuicao(ocorrencia_id, user_id, detalhe_dialog)).style(
                    "color: white; font-weight: bold; background-color: #008B8B !important;"
                ).classes("text-white font-bold px-4 py-2 w-32 text-center")

    confirm_dialog.open()


# ------------------------------------------ SALVA NO BANCO  ----------------------------------------

def salvar_atribuicao(ocorrencia_id, responsavel_id, detalhe_dialog):
    if responsavel_id:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE ocorrencias 
            SET responsavel_id = %s, 
                status = 'Em espera' 
            WHERE id = %s
        """, (responsavel_id, ocorrencia_id))
        conn.commit()

        cursor.close()
        conn.close()
        detalhe_dialog.close()

        ui.notify("Ocorrência atribuída com sucesso!", type="positive")
    else:
        ui.notify("Por favor, selecione um responsável!", type="warning")


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

# ------------------------------------------- EXCLUI OCORRENCIAS -----------------------------------------

def excluir_ocorrencia(ocorrencia_id, detalhe_dialog, confirm_dialog=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM ocorrencias WHERE id = %s", (ocorrencia_id,))
        ocorrencia = cursor.fetchone()

        if not ocorrencia:
            ui.notify("[ERRO] Ocorrência não encontrada!", type="warning")
            return

        cursor.execute("DELETE FROM ocorrencias WHERE id = %s", (ocorrencia_id,))
        conn.commit()

        if confirm_dialog:
            confirm_dialog.close()
        if detalhe_dialog:
            detalhe_dialog.close()

        ui.notify("Ocorrência excluída com sucesso!", type="positive")

    except Exception as e:
        ui.notify(f"[ERRO] Erro ao excluir ocorrência: {e}", type="warning")

    finally:
        conn.close()
        cursor.close()

# -------------------------------------- CONFIRMA EXCLUI OCORRENCIAS -----------------------------------

def confirmar_excluir_ocorrencia(ocorrencia_id, detalhe_dialog):
    with ui.dialog() as confirm_dialog:
        with ui.card().style('background-color: #ffffff !important;').classes("w-96 mx-auto"):
            ui.label("⚠️ Tem certeza que deseja excluir esta ocorrência?").classes("text-lg font-bold text-center")

            with ui.row().classes("w-full flex justify-center items-center q-mt-md gap-4"):
                ui.button("Não", on_click=confirm_dialog.close).style(
                    "color: white; font-weight: bold; background-color: #FF6347 !important;"
                ).classes("w-32")

                ui.button("Sim", on_click=lambda: excluir_ocorrencia(ocorrencia_id, detalhe_dialog, confirm_dialog)).style(
                    "color: white; font-weight: bold; background-color: #008B8B !important;"
                ).classes("w-32")

    confirm_dialog.open()