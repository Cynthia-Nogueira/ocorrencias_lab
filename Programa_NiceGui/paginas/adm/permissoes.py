from nicegui import ui, app
from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection

# -------------------------------- xxxxxxxxxxxxxxxxxxxx ----------------------------------------

def atribui_ocorrencias(ocorrencia):
    pass



# ----------------------------------------- CONFIRMA A ESCOLHA DO USER --------------------------------------------

def confirma_atribuicao(ocorrencia_id, user_id, admin_id, atribuir_ocorrencia_dialog):
    atribui_ocorrencias(ocorrencia_id, user_id, admin_id)
    ui.notify("✅ Ocorrência atribuída com sucesso!", type="positive")
    atribuir_ocorrencia_dialog.close()


# -------------------------------- RECUPERA OCORRENCIAS CANCELADAS -----------------------------

# ---------------------------------- CONFIRMA A RESTAURACAO OCORRENCIA ----------------------------------------

def confirmar_restauracao(ocorrencia_id, dialog):
    with ui.dialog() as confirm_dialog:
        with ui.card():
            ui.label("Deseja realmente restaurar esta ocorrência para 'Não atribuída'?").classes("text-lg font-bold")
            with ui.row().classes("justify-end gap-4 q-mt-md"):
                ui.button("Não", on_click=confirm_dialog.close)
                ui.button("Sim", on_click=lambda: restaurar_ocorrencia(ocorrencia_id, confirm_dialog, dialog))

        confirm_dialog.open()

# ---------------------------------- RESTAURA A OCORRENCIA ----------------------------------------

def restaurar_ocorrencia(ocorrencia_id, confirm_dialog, detalhe_dialog):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE ocorrencias
            SET status = 'Não atribuída', responsavel = NULL, responsavel_id = NULL, data_status_alterado = NOW()
            WHERE id = %s
        """, (ocorrencia_id,))
        conn.commit()

        ui.notify("Ocorrência restaurada com sucesso!", type="positive")
        confirm_dialog.close()
        detalhe_dialog.close()

    except Exception as e:
        ui.notify(f"Erro ao restaurar: {str(e)}", type="negative")
    finally:
        cursor.close()
        conn.close()