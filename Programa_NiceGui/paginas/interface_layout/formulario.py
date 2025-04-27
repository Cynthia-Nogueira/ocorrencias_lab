from nicegui import app, ui
from datetime import date, datetime
from Programa_NiceGui.paginas.banco_dados.db_conection import obter_user_logado, get_db_connection
from Programa_NiceGui.paginas.notificacoes_servicos.utilizadores import obter_lista_user
from Programa_NiceGui.paginas.notificacoes_servicos.notificacao_utils import enviar_notificacao
from Programa_NiceGui.paginas.notificacoes_servicos.ocorrencias import salvar_ocorrencia, ultima_ocorrencia_id

# ------------------------------------------- ESTRUTURA FORMULARIO -------------------------------------------

def novo_formulario():
    app.add_static_files('/static', '../static')
    ui.add_head_html('<script src="/static/js/scripts.js"></script>')

    with ui.dialog() as dialog, ui.card().classes("w-4/5 h-[600px] mx-auto"):    #h530
        ui.label("Nova Ocorrência").classes("text-2xl mx-auto font-bold mb-4")

        with ui.row().classes("w-full justify-between"):
            with ui.grid(columns=2).classes("w-full"):
                cliente = ui.input("Cliente").classes("w-full")
                num_processo = ui.input("Nº Processo").classes("w-full")

        hoje = date.today().strftime("%d/%m/%Y")

        with ui.row().classes("w-full justify-between"):
            with ui.grid(columns=2).classes("w-full"):
                with ui.input('Data', value=hoje).props("readonly") as date_input:
                    with ui.menu().props('no-parent-event') as menu:
                        with ui.date().bind_value(date_input).style(
                                "--q-primary:#008B8B; --q-color-calendar-header:#008B8B;"):
                            with ui.row().classes('justify-end'):
                                ui.button('Fechar', on_click=menu.close).props('flat').style("color:#0a0476;")
                    with date_input.add_slot('prepend'):
                        ui.icon('edit_calendar', color="#008B8B").on('click', menu.open).classes(
                            'cursor-pointer w-full')

                status = ui.input("Status", value="Não atribuída").props("readonly").classes("w-full")

        titulo = ui.input("Título").props("maxlength=400").style("background-color: transparent !important; "
                                          "box-shadow: none !important;").classes("w-full mr-2")
        conteudo = ui.textarea("Conteúdo da ocorrência").props("maxlength=400").classes("w-full mr-2")
        contador = ui.label("0/400 caracteres").classes("text-sm text-gray-500 mb-4")

        def atualizar_contador():
            carac_digitado = len(conteudo.value)
            contador.set_text(f"{carac_digitado}/400 caracteres")
            if carac_digitado >= 400:
                contador.classes(replace="text-sm text-red-500 mb-4")
            else:
                contador.classes(replace="text-sm text-gray-500 mb-4")

        conteudo.on("keydown", lambda: atualizar_contador())

        atualizar_contador()

        current_user_id = app.storage.user.get("userid", None)
        nome_user = obter_user_logado(current_user_id)

        def btn_salvar():

            #Salva a ocorrência e envia notificações para outros usuários
            if not conteudo.value.strip():
                ui.notify("O campo 'Conteúdo da ocorrência' é obrigatório.", type="negative")
                return

            if not titulo.value.strip():
                ui.notify("O campo 'Título' é obrigatório.", type="negative")
                return

            # Converter a data para o formato correto para o banco de dados (YYYY-MM-DD)
            try:
                data_formatada = datetime.strptime(date_input.value, "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError as e:
                ui.notify(f"Erro ao formatar a data: {e}", type="negative")
                return

            # chama a função de salvar com a data formatada corretamente
            try:
                msg, sucesso = salvar_ocorrencia(cliente.value, num_processo.value, data_formatada,
                                                 status.value, titulo.value, conteudo.value, app)
            except Exception as e:
                ui.notify(f"Erro ao salvar: {e}. Verifique os dados preenchidos.", type="negative")
                return

            if sucesso:
                ui.notify(msg, type="positive")
                lista_user = obter_lista_user()    #obtem todos os usuarios para notificar

                if not nome_user:
                    ui.notify("Utilizador logado não encontrado.", type="negative")
                    return

                # Criando a notificação formatada
                mensagem_notificacao = (
                    f"🟠 Nova ocorrência registada por:\n"
                    f"  {nome_user}\n"
                )

                # Enviar a notificação para os usuários, excluindo o usuário logado
                for user in lista_user:
                    if user['id'] != current_user_id:
                        enviar_notificacao(user['id'], mensagem_notificacao, ultima_ocorrencia_id())

                # Limpa os campos do formulário
                cliente.set_value("")
                num_processo.set_value("")
                date_input.set_value(date.today().strftime("%d/%m/%Y"))
                titulo.set_value("")
                conteudo.set_value("")
                status.set_value("Não atribuída")

                atualizar_contador()

            else:
                ui.notify(msg, type="negative")


        with ui.row().classes("mx-auto gap-x-8"):
            ui.button("Cancelar", on_click=dialog.close).style("color: white; font-weight: bold;"
                            " background-color: #E73B3B !important;").classes( "btn-secondary w-32")

            ui.button("Salvar", on_click=btn_salvar).style("color: white; font-weight: bold; "
                            "background-color: #008B8B !important;").classes("btn-primary w-32")


    dialog.open()

# ------------------------------------ FORM PARA EDITAR AS OCORRENCIAS ----------------------------------

def abrir_formulario_edicao(ocorrencia):
    ocorrencia_id, cliente_valor, num_processo_valor, responsavel, responsavel_id, data_valor, status_valor, titulo_valor, conteudo_valor, criador_id = ocorrencia

    with ui.dialog() as dialog_edicao, ui.card().classes("w-4/5 h-[600px] mx-auto"):
        ui.label("Editar Ocorrência").classes("text-2xl mx-auto font-bold mb-4")

        with ui.row().classes("w-full justify-between"):
            with ui.grid(columns=2).classes("w-full"):
                cliente = ui.input("Cliente", value=cliente_valor).classes("w-full")
                num_processo = ui.input("Nº Processo", value=num_processo_valor).classes("w-full")

        data_formatada = data_valor.strftime("%d/%m/%Y") if isinstance(data_valor, datetime) else data_valor

        with ui.row().classes("w-full justify-between"):
            with ui.grid(columns=2).classes("w-full"):
                ui.input("Data", value=data_formatada).props("readonly").classes("w-full")
                ui.input("Status", value=status_valor).props("readonly").classes("w-full")

        titulo = ui.input("Título", value=titulo_valor).props("maxlength=400").classes("w-full mr-2")
        conteudo = ui.textarea("Conteúdo da ocorrência", value=conteudo_valor).props("maxlength=400").classes("w-full mr-2")
        contador = ui.label("0/400 caracteres").classes("text-sm text-gray-500 mb-4")

        def atualizar_contador():
            carac_digitado = len(conteudo.value)
            contador.set_text(f"{carac_digitado}/400 caracteres")
            contador.classes(replace="text-sm text-red-500 mb-4" if carac_digitado >= 400 else "text-sm text-gray-500 mb-4")

        conteudo.on("keydown", lambda: atualizar_contador())
        atualizar_contador()

        def salvar_edicao():
            if not titulo.value.strip() or not conteudo.value.strip():
                ui.notify("Preencha os campos obrigatórios: Título e Conteúdo.", type="negative")
                return

            # Exibir a caixa de confirmação antes de salvar
            mostra_confirmacao_edicao(
                ocorrencia_id,
                cliente.value,
                num_processo.value,
                titulo.value,
                conteudo.value,
                dialog_edicao
            )

        with ui.row().classes("mx-auto gap-x-8"):
            ui.button("Cancelar", on_click=dialog_edicao.close).style(
                "color: white; font-weight: bold; background-color: #E73B3B !important;").classes("btn-secondary w-32")

            ui.button("Salvar", on_click=salvar_edicao).style(
                "color: white; font-weight: bold; background-color: #008B8B !important;").classes("btn-primary w-32")


        dialog_edicao.open()


# ----------------------------------- SALVA AS ALTERACOES ------------------------------------

def salvar_alteracoes_ocorrencia(ocorrencia_id, cliente, num_processo, titulo, conteudo):
    from Programa_NiceGui.paginas.interface_layout.menu import refresh_lista_ocorrencias
    global status_global
    global condicao_extra_global

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Atualiza a ocorrência no banco de dados
        cursor.execute("""
            UPDATE ocorrencias
            SET cliente = %s,
                num_processo = %s,
                titulo = %s,
                conteudo = %s
            WHERE id = %s;
        """, (cliente, num_processo, titulo, conteudo, ocorrencia_id))
        conn.commit()
    except Exception as e:
        ui.notify(f"Erro ao atualizar a ocorrência: {e}", type="negative")
    finally:
        cursor.close()
        conn.close()

# -----------------------------------  MOSTRAR CONFIRMACAO EDICAO ------------------------------------

def mostra_confirmacao_edicao(ocorrencia_id, cliente, num_processo, titulo, conteudo, dialog_edicao):
    from Programa_NiceGui.paginas.interface_layout.menu import refresh_lista_ocorrencias
    import Programa_NiceGui.paginas.interface_layout.global_state as global_state

    global_state.cliente_label = cliente
    global_state.num_processo_label = num_processo
    global_state.titulo_label = titulo
    global_state.conteudo_label = conteudo

    with (ui.dialog() as confirm_dialog):
        with ui.card().style('background-color: #ebebeb !important;').classes("w-96 mx-auto"):
            ui.label("Tem certeza que deseja salvar as alterações?").classes(
                "text-lg font-bold mx-auto q-mb-sm text-center")

            with ui.row().classes("w-full flex justify-center items-center q-mt-md gap-4"):
                ui.button("Não", on_click=confirm_dialog.close).style(
                    "color: white; font-weight: bold; background-color: #FF6347 !important;").classes(
                    "text-white font-bold px-4 py-2 w-32 text-center")

                ui.button("Sim", on_click=lambda: (
                    salvar_alteracoes_ocorrencia(ocorrencia_id, cliente, num_processo, titulo, conteudo),
                    ui.notify("Ocorrência atualizada com sucesso!", type="positive"),
                    confirm_dialog.close(),
                    dialog_edicao.close(),
                    refresh_lista_ocorrencias()
                )).style("color: white; font-weight: bold; background-color: #008B8B !important;").classes(
                    "text-white font-bold px-4 py-2 w-32 text-center")

        confirm_dialog.open()


