from nicegui import ui, app
from datetime import datetime
from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection
from Programa_NiceGui.paginas.interface_layout.page_user import carregar_ocorrencias_user
from Programa_NiceGui.paginas.notificacoes_servicos.helper_notificacoes import atribui_nome_usuario
from Programa_NiceGui.paginas.notificacoes_servicos.notificacoes import notifica_ocorrencia_devolvida, \
    notifica_ocorrencia_cancelada, notifica_ocorrencias_concluidas


#------------------------------------ DEVOLVE A OCORRENCIA DO USER ----------------------------

def confirmar_devolucao_cacelamento(ocorrencia_id, detalhe_dialog):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Atualiza os campos no banco
        cursor.execute("""
            UPDATE ocorrencias
            SET responsavel = NULL, responsavel_id = NULL, status = 'Devolvida'
            WHERE id = %s
        """, (ocorrencia_id,))
        conn.commit()

        ui.notify("Ocorrência devolvida com sucesso!", type="warning")

        # notifica todos os usuários
        nome_usuario = atribui_nome_usuario()

        notifica_ocorrencia_devolvida(ocorrencia_id, nome_usuario)
        notifica_ocorrencia_cancelada(ocorrencia_id, nome_usuario)

        # Fecha o diálogo de detalhes
        detalhe_dialog.close()

        # Atualiza a lista do user
        carregar_ocorrencias_user()

    finally:
        cursor.close()
        conn.close()


# ---------------------------------- ATUALIZA STATUS -------------------------------

def atualiza_status(ocorrencia_id, novo_status):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if novo_status == "Devolvida":
            #  atualiza status e remove responsavel
            cursor.execute("""
                UPDATE ocorrencias
                SET status = %s, 
                    responsavel_id = NULL,
                    data_aceite = %s,
                    data_status_alterado = %s
                WHERE id = %s
            """, (novo_status, datetime.now(), datetime.now(), ocorrencia_id))


        elif novo_status == "Em Espera":
            # Atualiza o status para 'Em Espera' e também atualiza data_status_alterado
            cursor.execute("""
                UPDATE ocorrencias
                SET status = %s, 
                    data_status_alterado = %s
                WHERE id = %s
            """, (novo_status, datetime.now(), ocorrencia_id))

        elif novo_status == "Em Execução":
            # Atualiza o status para 'Em execucao' e também atualiza data_status_alterado
            cursor.execute("""
                UPDATE ocorrencias
                SET status = %s, 
                    data_status_alterado = %s
                WHERE id = %s
            """, (novo_status, datetime.now(), ocorrencia_id))

        elif novo_status == "Concluída":
            # Atualiza o status para 'Concluída' e também atualiza data_status_alterado
            cursor.execute("""
                UPDATE ocorrencias
                SET status = %s, 
                    data_status_alterado = %s
                WHERE id = %s
            """, (novo_status, datetime.now(), ocorrencia_id))

        elif novo_status == "Cancelada":
            # Atualiza o status para 'Cancelada', remove o responsável e atualiza a data de alteração de status
            cursor.execute("""
                UPDATE ocorrencias
                SET status = %s,
                    responsavel_id = NULL,  
                    data_status_alterado = %s
                WHERE id = %s
            """, (novo_status, datetime.now(), ocorrencia_id))

        else:
            # Atualiza apenas o status
            cursor.execute("""
                UPDATE ocorrencias
                SET status = %s
                WHERE id = %s
            """, (novo_status, ocorrencia_id))

        conn.commit()

        nome_usuario = atribui_nome_usuario()

        # Notificação para todos os usuários quando for devolvida
        if novo_status == "Devolvida":
            notifica_ocorrencia_devolvida(ocorrencia_id, nome_usuario)
            ui.notify("🔄 Ocorrência devolvida com sucesso!", type="positive")

        elif novo_status == "Cancelada":
            notifica_ocorrencia_cancelada(ocorrencia_id, nome_usuario)
            ui.notify("❌ Ocorrência cancelada com sucesso!", type="positive")

        elif novo_status == "Concluída":
            notifica_ocorrencias_concluidas(ocorrencia_id, novo_status, nome_usuario)
            ui.notify(f"✨ Ocorrência concluída!", type="positive")

        elif novo_status == "Em Execução":
            ui.notify("🔧 Ocorrência em execução!", type="positive")

        elif novo_status == "Em Espera":
            ui.notify("⏳ Ocorrência em espera!", type="positive")

        else:
            ui.notify(f"📌 Status alterado para {novo_status}.", type="positive")

    except Exception as e:
        ui.notify(f"⚠️ Erro ao atualizar status: {e}", type="negative")
    finally:
        cursor.close()
        conn.close()

# --------------------------------- CONFIRMA A ALTERACAO PARA OS USERS --------------------------------

def confirmar_alteracao_status(ocorrencia_id, novo_status, detalhe_dialog):
    with ui.dialog() as confirm_dialog:
        with ui.card().style('background-color: #ebebeb !important;').classes("w-96 mx-auto"):
            ui.label(f"Tem certeza que deseja alterar o status para '{novo_status}'?").classes(
                "text-lg font-bold mx-auto q-mb-sm text-center")

            with ui.row().classes("w-full flex justify-center items-center q-mt-md gap-4"):
                ui.button("Não", on_click=confirm_dialog.close).style(
                    "color: white; font-weight: bold; background-color: #FF6347 !important;"
                ).classes("text-white font-bold px-4 py-2 w-32 text-center")

                ui.button("Sim",
                          on_click=lambda: [
                              atualiza_status(ocorrencia_id, novo_status),
                              confirm_dialog.close(),
                              detalhe_dialog.close()
                          ]).style(
                    "color: white; font-weight: bold; background-color: #008B8B !important;"
                ).classes("text-white font-bold px-4 py-2 w-32 text-center")


    confirm_dialog.open()