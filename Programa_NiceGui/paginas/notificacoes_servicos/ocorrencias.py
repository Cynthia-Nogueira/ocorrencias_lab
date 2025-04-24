import traceback
from nicegui import ui
from datetime import datetime
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

# ----------------------------- Cria uma nova ocorrência no banco -------------------------

def nova_ocorrencia(cliente, num_processo, data, status, titulo, conteudo, app):
    from Programa_NiceGui.paginas.notificacoes_servicos.notificacao_utils import enviar_notificacao

    criador_id = app.storage.user.get("userid", None)

    print("RESULTADO", criador_id)

    if not criador_id:
        raise Exception("Erro: Não foi possível identificar o usuário logado.")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
            INSERT INTO ocorrencias (cliente, num_processo, data, status, titulo, conteudo, criador_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """
        cursor.execute(query, (cliente, num_processo, data, status, titulo, conteudo, criador_id))
        ocorrencia_id = cursor.fetchone()[0]
        conn.commit()

        # Buscar todos os usuários, exceto o criador da ocorrência
        query_usuarios = "SELECT id FROM utilizador WHERE id != %s"
        cursor.execute(query_usuarios, (criador_id,))
        usuarios = cursor.fetchall()

        mensagem = f"Nova ocorrência registada: {cliente} - processo {num_processo}."

        for usuario in usuarios:
            enviar_notificacao(usuario[0], mensagem, ocorrencia_id)

    except Exception as e:
        print("Ocorreu um erro ao salvar a ocorrência:")
        print(traceback.format_exc())  # Exibe o traceback caso de erro

    finally:
        cursor.close()
        conn.close()

# ------------------------------------- SALVA FORMULÁRIO ----------------------------------------

def salvar_ocorrencia(cliente, num_processo, data_formatada, status, titulo, conteudo, app):
    if len(conteudo) > 400:
        return "Erro: o campo não pode exceder 400 caracteres."

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # data convertida para datetime com a hora atual
        if isinstance(data_formatada, str):
            data_formatada = datetime.strptime(data_formatada, "%Y-%m-%d")
            data_formatada = datetime.combine(data_formatada, datetime.now().time())

        # caso a data ja esteja formatada
        elif isinstance(data_formatada, datetime):
            if data_formatada.hour == 0 and data_formatada.minute == 0 and data_formatada.second == 0:
                data_formatada = datetime.combine(data_formatada.date(), datetime.now().time())



        criador_id = app.storage.user.get("userid", None)

        print("CRIADOR ID:", criador_id)

        if not criador_id:
            raise Exception("Usuário não identificado!")



        # consulta de inserção
        insert_stmt = (
            "INSERT INTO ocorrencias "
            "(cliente, num_processo, data, status, titulo, conteudo, criador_id)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )

        #valores da tabela
        cont = (cliente, num_processo, data_formatada, status, titulo, conteudo, criador_id)
        cursor.execute(insert_stmt, cont)
        conn.commit()

        return "Ocorrência salva com sucesso!", True

    except Exception as e:
        # caso ocorra erro exibe o erro completo, para depurar
        print("Ocorreu um erro ao salvar a ocorrência:")
        print(traceback.format_exc())

        ui.notify(f"Erro ao salvar ocorrência: {e}. Verifique os dados preenchidos.", color="red")
        return "Erro ao salvar ocorrência.", False

    finally:
        cursor.close()
        conn.close()


# ---------------------------------- BD lista ocorrencias ---------------------------------------------------

def obter_ocorrencias():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
        SELECT id, cliente, num_processo, responsavel, data, status, titulo, conteudo
        FROM ocorrencias
        WHERE status IN ('Devolvida', 'Não Atribuída', 'Em espera', 'Cancelada', 'Expirada')
        ORDER BY data DESC
        """
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
        cursor.execute("SELECT id, cliente, num_processo, data, titulo, conteudo, status FROM ocorrencias WHERE id = %s", (id_,))
        ocorrencia = cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if conn:
           conn.close()

    if ocorrencia:
        id_, cliente, num_processo, data, titulo, conteudo, status = ocorrencia

        with ui.dialog() as dialog, ui.card():
            ui.label(f"Editar Ocorrência #{id_}").classes("text-2xl font-bold mb-4")

            cliente_input = ui.input("Cliente", value=cliente).classes("w-full")
            num_processo_input = ui.input("Nº Processo", value=num_processo).classes("w-full")
            data_picker = ui.date(label="Data", value=data).classes("w-full")
            titulo_input = ui.input("Título", value=conteudo).classes("w-full")
            conteudo_input = ui.textarea("Conteúdo", value=conteudo).classes("w-full")
            status_input = ui.select(["Em espera", "Em execução", "Concluída", "Devolvida"], label="Status", value=status).classes(
                "w-full")

            def btn_salvar():
                try:
                    # salva a ocorrencia no banco
                    update_ocorrencia(id_, cliente_input.value,
                                      data_picker.value, titulo_input.value, conteudo_input.value,
                                      status_input.value)

                    # ntificacao de sucesso
                    ui.notify("Salvo com sucesso!", type="success")

                    # limpa os campos do form
                    cliente_input.set_value("")
                    num_processo_input.set_value("")
                    data_picker.set_value(None)
                    titulo_input.set_value("")
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


# ------------------------------  DEF PARA PEGAR A ULTIMA ID CRIADA ---------------------------------

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







