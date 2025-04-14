from nicegui import ui
from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection
from Programa_NiceGui.paginas.interface_layout.page_user import carregar_ocorrencias_user


#------------------------------------ DEVOLVE A OCORRENCIA DO USER ----------------------------

def devolver_ocorrencia(ocorrencia_id, detalhe_dialog):
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

        detalhe_dialog.close()

        # Atualiza a lista principal
        carregar_ocorrencias_user("Devolvida", "Ocorrências Devolvidas")

    finally:
        cursor.close()
        conn.close()


# --------------------------------------- CONFIRMA A DEVOLUCAO --------------------------------------


def confirma_devolucao(ocorrencia_id, detalhe_dialog):

    with ui.dialog() as dialog_confirmacao:
        with ui.card().classes("w-96 mx-auto q-pa-md").style("background-color: #fff3cd;"):
            ui.label("⚠️ Tem certeza que deseja devolver essa ocorrência?").classes("text-md font-bold text-center")

            with ui.row().classes("justify-around mt-4"):
                ui.button("Não", on_click=dialog_confirmacao.close)

                ui.button("Sim", on_click=lambda:[devolver_ocorrencia(ocorrencia_id, detalhe_dialog),
                                                            dialog_confirmacao.close()
                                                            ]).style("background-color: #ff6b6b; color: white; font-weight: bold;")

    dialog_confirmacao.open()


