import mysql
from nicegui import ui
from datetime import datetime

from Programa_NiceGui.paginas.funcoes_menu import enviar_notificacao
from db_conection import get_db_connection


# ------------------------------- Atualiza a ocorrência no banco --------------------------------

def update_ocorrencia(id, cliente, num_processo, responsavel, data, status, conteudo):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
            UPDATE ocorrencias 
            SET cliente = %s, num_processo = %s, responsavel = %s, data = %s, status = %s, conteudo = %s
            WHERE id = %s
        """
        cursor.execute(query, (id, cliente, num_processo, responsavel, data, status, conteudo))
        conn.commit()

    finally:
        cursor.close()
        conn.close()


# ---------------------------------- BD lista ocorrencias ---------------------------------------------------

def get_ocorrencias():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "SELECT * FROM ocorrencias"
        cursor.execute(query)
        ocorrencias = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()
        return ocorrencias


# ------------------------------------- Exclui ocorrência -----------------------------------------

def excluir_ocorrencia(id_):

    # msg para confirmar exclusao
    confirmacao = ui.confirm(f"Tem certeza que deseja excluir esta ocorrência? Esta ação não pode ser desfeita.")

    if not confirmacao:
        ui.notify("Exclusão cancelada.", type="negative")
        return False

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "DELETE FROM ocorrencias WHERE id = %s"
        cursor.execute(query, (id_,))
        conn.commit()
        ui.notify("Ocorrência excluida com sucesso!", type="positive")
        return True

    except Exception as e:
        ui.notify(f"Erro ao excluir ocorrência: {e}", color="red")  # Notificação de erro
        return False

    finally:
        cursor.close()
        conn.close()


# ---------------------------------------- UPDATE STATUS ---------------------------------------
"""def update_status(id_, novo_status):
    # Implementa a atualização no banco de dados
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            #UPDATE ocorrencias
            #SET status = %s
            #WHERE id = %s
""", (novo_status, id_))
        conn.commit()
    except Exception as e:
        ui.notify(f"Erro ao atualizar status: {e}", color="red")
    finally:
        cursor.close()
        conn.close()"""

# ----------------------------- Cria uma nova ocorrência no banco -------------------------

def nova_ocorrencia(cliente, num_processo, responsavel, data, status, conteudo):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
                INSERT INTO ocorrencias (cliente, num_processo, responsavel, data, status, conteudo)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """
        cursor.execute(query, (cliente, num_processo, responsavel, data, status, conteudo))
        ocorrencia_id = cursor.fetchone()[0]  #pega o id da ocorrencia inserida
        conn.commit()

        #busca todos que estao registados em utilizador
        query_usuarios = """SELECTE id, nome, apelido FROM utilizador"""

        cursor.execute(query_usuarios)
        usuarios = cursor.fetchall()  #cria uma lista de tuplas com o id, nome e apelido

        mensagem = f"Nova ocorrencia registada: {cliente} - processo {num_processo}."

        for usuario in usuarios:
            nome_completo = f"{usuario[1]} {usuario[2]}"
            enviar_notificacao(usuario[0], mensagem)

    finally:
        cursor.close()
        conn.close()


# ------------------------------------- Exclui ocorrência -----------------------------------------

def excluir_ocorrencia(id):

    # msg para confirmar exclusao
    confirmacao = ui.confirm(f"Tem certeza que deseja excluir esta ocorrência? Esta ação não pode ser desfeita.")

    if not confirmacao:
        ui.notify("Exclusão cancelada.", type="negative")
        return False

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "DELETE FROM ocorrencias WHERE id = %s"
        cursor.execute(query, (id,))
        conn.commit()
        ui.notify("Ocorrência excluida com sucesso!", type="positive")
        return True

    except Exception as e:
        ui.notify(f"Erro ao excluir ocorrência: {e}", color="red")  # Notificação de erro
        return False

    finally:
        cursor.close()
        conn.close()


# ------------------------------------- Editar ocorrência -----------------------------------------


def formulario_edicao(id_):
    #abre a ocorrência selecionada para edição
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ocorrencias WHERE id = %s", (id,))
    ocorrencia = cursor.fetchone()
    cursor.close()
    conn.close()

    if ocorrencia:
        id_, cliente, num_processo, responsavel, data, conteudo, status = ocorrencia

        with ui.dialog() as dialog, ui.card():
            ui.label(f"Editar Ocorrência #{id_}").classes("text-2xl font-bold mb-4")

            cliente_input = ui.input("Cliente", value=cliente).classes("w-full")
            num_processo_input = ui.input("Nº Processo", value=num_processo).classes("w-full")
            responsavel_input = ui.select(["Ana", "Carlos", "João", "Maria"], label="Responsável",
                                          value=responsavel).classes("w-full")
            data_picker = ui.date(label="Data", value=data).classes("w-full")
            conteudo_input = ui.textarea("Conteúdo", value=conteudo).classes("w-full")
            status_input = ui.select(["Em espera", "Em execução", "Concluído"], label="Status", value=status).classes(
                "w-full")

            def btn_salvar():
                try:
                    # salva a ocorrencia no banco
                    update_ocorrencia(id_, cliente_input.value,
                                      num_processo_input.value, responsavel_input.value,
                                      data_picker.value, conteudo_input.value,
                                      status_input.value)

                    # ntificacao de sucesso
                    ui.notify("Salvo com sucesso!", type="success")

                    # limpa os campos do form
                    cliente_input.set_value("")
                    num_processo_input.set_value("")
                    responsavel_input.set_value(None)
                    data_picker.set_value(None)
                    conteudo_input.set_value("")
                    status_input.set_value(None)

                except Exception as e:
                    # notificação se houver erro
                    ui.notify(f"Erro ao salvar: {str(e)}", type="negative")

            with ui.row().classes("justify-end mt-4"):
                ui.button("Salvar", on_click=btn_salvar).classes("btn-primary")
                ui.button("Cancelar", on_click=lambda: dialog.close()).classes("btn-secondary")

        dialog.open()


# ------------------------------------- SALVA FORMULÁRIO ----------------------------------------

def salvar_ocorrencia(cliente, num_processo, responsavel, data, status, conteudo):

    if len(conteudo) > 400:
        return "Erro: o campo não pode exceder 400 caracteres."

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        insert_stmt=("INSERT INTO ocorrencias "
                       "(cliente, num_processo, responsavel, data, status, conteudo)"
                       "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        #valores que vao entrar na tabela
        cont = (cliente, num_processo, responsavel, data, status, conteudo)
        cursor.execute(insert_stmt, cont)
        conn.commit()
        return "Ocorrência salva com sucesso!", True

    except Exception as e:
        return f"Erro ao salvar ocorrência: {e}", False

    finally:
        cursor.close()
        conn.close()





