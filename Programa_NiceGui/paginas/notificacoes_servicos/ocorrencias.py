from nicegui import ui
from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection

# ------------------------------- Atualiza a ocorrência no banco --------------------------------

def update_ocorrencia(id, cliente, num_processo, data, status, conteudo):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
            UPDATE ocorrencias 
            SET cliente = %s, num_processo = %s, data = %s, status = %s, conteudo = %s
            WHERE id = %s
        """
        cursor.execute(query, (id, cliente, num_processo, data, status, conteudo))
        conn.commit()

    finally:
        cursor.close()
        conn.close()


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

# ----------------------------- Cria uma nova ocorrência no banco -------------------------

def nova_ocorrencia(cliente, num_processo, data, status, conteudo, usuario_criador):

    from Programa_NiceGui.paginas.notificacoes_servicos.notificacao_utils import enviar_notificacao

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
            INSERT INTO ocorrencias (cliente, num_processo, data, status, conteudo, criador_id)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """
        cursor.execute(query, (cliente, num_processo, data, status, conteudo, usuario_criador))
        ocorrencia_id = cursor.fetchone()[0]
        conn.commit()

        # Buscar todos os usuários, exceto o criador da ocorrência
        query_usuarios = "SELECT id FROM utilizador WHERE id != %s"
        cursor.execute(query_usuarios, (usuario_criador,))
        usuarios = cursor.fetchall()

        mensagem = f"Nova ocorrência registrada: {cliente} - processo {num_processo}."

        for usuario in usuarios:
            enviar_notificacao(usuario[0], mensagem, ocorrencia_id)

    finally:
        cursor.close()
        conn.close()


# ------------------------------------- SALVA FORMULÁRIO ----------------------------------------

def salvar_ocorrencia(cliente, num_processo, data_formatada, status, conteudo):

    if len(conteudo) > 400:
        return "Erro: o campo não pode exceder 400 caracteres."

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        insert_stmt=("INSERT INTO ocorrencias "
                       "(cliente, num_processo, data, responsavel, status, conteudo)"
                       "VALUES (%s, %s, %s, NULL, %s, %s)"
        )
        #valores que vao entrar na tabela
        cont = (cliente, num_processo, data_formatada, status, conteudo)
        cursor.execute(insert_stmt, cont)
        conn.commit()
        return "Ocorrência salva com sucesso!", True

    except Exception as e:
        return f"Erro ao salvar ocorrência: {e}", False

    finally:
        cursor.close()
        conn.close()


# ---------------------------------- BD lista ocorrencias ---------------------------------------------------

def obter_ocorrencias():
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


# ------------------------------------- Editar ocorrência -----------------------------------------


def formulario_edicao(id_):
    #abre a ocorrência selecionada para edição
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ocorrencias WHERE id = %s", (id_,))
        ocorrencia = cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if conn:
           conn.close()

    if ocorrencia:
        id_, cliente, num_processo, data, conteudo, status = ocorrencia

        with ui.dialog() as dialog, ui.card():
            ui.label(f"Editar Ocorrência #{id_}").classes("text-2xl font-bold mb-4")

            cliente_input = ui.input("Cliente", value=cliente).classes("w-full")
            num_processo_input = ui.input("Nº Processo", value=num_processo).classes("w-full")
            data_picker = ui.date(label="Data", value=data).classes("w-full")
            conteudo_input = ui.textarea("Conteúdo", value=conteudo).classes("w-full")
            status_input = ui.select(["Em espera", "Em execução", "Concluído"], label="Status", value=status).classes(
                "w-full")

            def btn_salvar():
                try:
                    # salva a ocorrencia no banco
                    update_ocorrencia(id_, cliente_input.value,
                                      data_picker.value, conteudo_input.value,
                                      status_input.value)

                    # ntificacao de sucesso
                    ui.notify("Salvo com sucesso!", type="success")

                    # limpa os campos do form
                    cliente_input.set_value("")
                    num_processo_input.set_value("")
                    data_picker.set_value(None)
                    conteudo_input.set_value("")
                    status_input.set_value(None)

                except Exception as e:
                    # notificação se houver erro
                    ui.notify(f"Erro ao salvar: {str(e)}", type="negative")

            with ui.row().classes("justify-end mt-4"):
                ui.button("Salvar", on_click=btn_salvar).style("color: white; font-weight: bold;"
                                    " background-color: #008B8B !important;").classes("btn-primary")
                ui.button("Cancelar", on_click=lambda: dialog.close()).style("color: white; font-weight: bold;"
                                    " background-color: #008B8B !important;").classes("btn-secondary")

        dialog.open()


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


# ------------------------------  DEF PARA OEGAR A ULTIMA ID CRIADA ---------------------------------

def ultima_ocorrencia_id():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Busca o último ID da tabela 'ocorrencias'
        query = "SELECT MAX(id) FROM ocorrencias;"
        cursor.execute(query)
        ocorrencia_id = cursor.fetchone()[0]  # Captura o ID obtido (ou None, caso não haja registros)

        return ocorrencia_id

    except Exception as e:
        print(f"Erro ao obter o ID da última ocorrência: {e}")
        return None

    finally:
        cursor.close()
        conn.close()
