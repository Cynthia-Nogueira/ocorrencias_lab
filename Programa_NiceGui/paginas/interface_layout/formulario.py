from nicegui import app, ui
from datetime import date, datetime
from Programa_NiceGui.paginas.banco_dados.db_conection import obter_user_logado
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
                                ui.button('Fechar', on_click=menu.close).props('flat').style("color:#008B8B;")
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

            if not conteudo.value.strip():  # Verifica se o campo está vazio
                ui.notify("O campo 'Conteúdo da ocorrência' é obrigatório.", type="negative")
                return

            if not titulo.value.strip():  # Verifica se o campo está vazio
                ui.notify("O campo 'Título' é obrigatório.", type="negative")
                return

            # Converter a data para o formato correto para o banco de dados (YYYY-MM-DD)
            try:
                data_formatada = datetime.strptime(date_input.value, "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError as e:
                ui.notify(f"Erro ao formatar a data: {e}", type="negative")
                return

            # Agora, chamamos a função de salvar com a data formatada corretamente

            try:
                msg, sucesso = salvar_ocorrencia(cliente.value, num_processo.value, data_formatada,
                                                 status.value, titulo.value, conteudo.value)
            except Exception as e:
                ui.notify(f"Erro ao salvar: {e}. Verifique os dados preenchidos.", type="negative")
                return

            if sucesso:
                ui.notify(msg, type="positive")

                # Obtém todos os usuários (exceto o usuário logado) para enviar a notificação
                lista_user = obter_lista_user()

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
            ui.button("Salvar", on_click=btn_salvar).style("color: white; font-weight: bold; "
                                    "background-color: #008B8B !important;").classes("btn-primary w-32")

            ui.button("Cancelar", on_click=dialog.close).style("color: white; font-weight: bold;"
                                    " background-color: #008B8B !important;").classes("btn-secondary w-32")

    dialog.open()

