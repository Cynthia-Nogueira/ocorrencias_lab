from nicegui import ui, app
from datetime import datetime
from Programa_NiceGui.paginas.adm.permissoes import confirmar_restauracao, confirma_atribuicao, confirmar_excluir_ocorrencia
from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection
from Programa_NiceGui.paginas.interface_layout.formulario import abrir_formulario_edicao
from Programa_NiceGui.paginas.notificacoes_servicos.notificacao_utils import carregar_notificacoes
from Programa_NiceGui.paginas.notificacoes_servicos.ocorrencias_utils import confirmar_alteracao_status
from Programa_NiceGui.paginas.notificacoes_servicos.utilizadores import utilizador_ativo

# --------------------------------- EXIBE AS NOTIFICACOES NO MENU ---------------------------

notificacao_elements = {}

def exibir_notificacoes_menu():
    from Programa_NiceGui.paginas.notificacoes_servicos.notificacoes import visualizar_notificacao
    global notificacoes
    global notificacao_elements
    notificacao_elements = {}
    current_user_id = app.storage.user.get("userid", None)

    if current_user_id:
        notificacoes, _ = carregar_notificacoes(current_user_id)

    with ui.dialog() as dialog:
        with ui.card().style("padding: 8px 0; background: #ececf5").classes("w-120 mx-auto") as card_notificacoes:
            card_notificacoes.style("background-color: #008B8B; border-radius: 10px; overflow-y: auto; width: 600px; height: 600px;")

            # Título fixo no topo
            with ui.row().classes("w-full justify-center items-center q-pa-sm").style("position: sticky; top: 0; background-color: #008B8B; z-index: 1;"):
                ui.label("Notificações").style("background-color: #008B8B; color: #fff8ff !important;").classes("text-2xl font-bold text-center")

            # Área scrollável com notificações
            with ui.scroll_area().style("flex-grow: 1; overflow-y: auto; background-color: #ececf5;").classes("w-full q-px-md q-pt-sm"):
                with ui.column().classes("w-full gap-2"):
                    for notificacao in notificacoes:
                        notificacao_id = notificacao["id"]
                        mensagem = notificacao["mensagem"]

                        notif_button = ui.button(mensagem).classes("q-pa-sm text-left full-width")
                        notificacao_elements[notificacao_id] = notif_button

                        notif_button.on('click', lambda e, id=notificacao_id: visualizar_notificacao(id, notificacao_elements))

                        if not notificacao["lida"]:
                            notif_button.style("color: #464646 !important; font-weight: bold; background-color: #D2E9DD !important;")
                        else:
                            notif_button.style("color: #808080 !important; font-weight: normal; background-color: #E5FCF2 !important;")

            # Botão fechar fixo no rodapé
            with ui.row().style("position: sticky; bottom: 0; background-color: #008B8B; z-index: 1;").classes("w-full justify-center q-pa-sm"):
                ui.button("Fechar", on_click=dialog.close).style(
                    "color: black !important; font-weight: bold; background-color: #fff8ff !important;"
                ).classes("text-white font-bold px-4 py-2")

        dialog.open()

# ----------------------------------- FILTRA AS OCORRENCIAS POR STATUS -------------------------------------

@ui.refreshable
def refreshable_ocorrencias_lista(ocorrencias):
    # processa as ocorrências
    with ui.column().classes("w-full gap-2"):
        for ocorrencia in ocorrencias:
            ui.button(
                f"{ocorrencia[3] or 'Não Atribuído'}: Cliente  {ocorrencia[1]} - Título:  '{ocorrencia[7]}'",
                on_click=lambda o=ocorrencia: detalhes_ocorrencia(o)).style(
                "color: #464646 !important; font-weight: bold; background-color: #D2E9DD !important;"
                ).classes("q-pa-sm text-left full-width")

refresh_lista_ocorrencias = refreshable_ocorrencias_lista.refresh


def ocorrencias_filtradas(status: str, titulo: str, condicao_extra: str = None):
    global refresh_lista_ocorrencias
    global status_global
    global condicao_extra_global
    status_global = status
    condicao_extra_global = condicao_extra
    conn = get_db_connection()
    cursor = conn.cursor()

    with ui.dialog() as dialog:
        with ui.card().style("padding: 8px 0;").classes("w-120 mx-auto") as card_notificacoes:
            card_notificacoes.style("background-color: #008B8B; border-radius: 10px; overflow-y: auto; width: 600px; height: 600px;")

            with ui.column().classes("w-full"):
                with ui.row().style("position: sticky; top: 0; background-color: #008B8B; z-index: 1;").classes("w-full justify-center items-center q-pa-sm"):
                    ui.label(titulo).style("background-color: #008B8B; color: #fff8ff !important;").classes("text-center font-bold text-2xl")

                # Scroll Area para as notificações
                with ui.scroll_area().style("flex-grow: 1; overflow-y: auto; background-color: #ececf5;").classes("w-full q-px-md q-pt-sm"):
                    with ui.column().classes("w-full gap-2"):
                        try:
                            if condicao_extra:
                                query = f"""
                                    SELECT id, cliente, num_processo, responsavel, responsavel_id, data, status, titulo, conteudo, criador_id
                                    FROM ocorrencias
                                    WHERE {condicao_extra}
                                    ORDER BY data DESC;
                                """
                                params = ()

                            else:
                                if status == "Em espera":
                                    query = """
                                        SELECT id, cliente, num_processo, responsavel, responsavel_id, data, status, titulo, conteudo, criador_id
                                        FROM ocorrencias
                                        WHERE responsavel IS NOT NULL AND status = 'Em espera'
                                        ORDER BY data_status_alterado DESC, data DESC;
                                    """
                                    params = ()

                                elif status == "Expirada":
                                    query = """
                                        SELECT id, cliente, num_processo, responsavel, responsavel_id, data, status, titulo, conteudo, criador_id
                                        FROM ocorrencias
                                        WHERE status = 'Expirada'
                                        ORDER BY data_status_alterado DESC, data DESC;
                                    """
                                    params = ()

                                elif status == "Devolvida":
                                    query = """
                                        SELECT id, cliente, num_processo, responsavel, responsavel_id, data, status, titulo, conteudo, criador_id
                                        FROM ocorrencias
                                        WHERE status = 'Devolvida'
                                        ORDER BY data_status_alterado DESC, data DESC;
                                    """
                                    params = ()

                                elif status == "Não atribuída":
                                    query = """
                                        SELECT id, cliente, num_processo, responsavel, responsavel_id, data, status, titulo, conteudo, criador_id
                                        FROM ocorrencias
                                        WHERE responsavel IS NULL AND status = 'Não atribuída'
                                        ORDER BY data_status_alterado DESC, data DESC;
                                    """
                                    params = ()

                                elif status == "Cancelada":
                                    query = """
                                        SELECT id, cliente, num_processo, responsavel, responsavel_id, data, status, titulo, conteudo, criador_id
                                        FROM ocorrencias
                                        WHERE responsavel IS NOT NULL AND status = 'Cancelada'
                                        ORDER BY data_status_alterado DESC, data DESC;
                                    """
                                    params = ()

                                elif status is None:
                                    query = """
                                        SELECT id, cliente, num_processo, responsavel, responsavel_id, data, status, titulo, conteudo, criador_id
                                        FROM ocorrencias
                                        WHERE status IS NULL
                                        ORDER BY data_status_alterado DESC, data DESC;
                                    """
                                    params = ()

                                else:
                                    query = """
                                        SELECT id, cliente, num_processo, responsavel, responsavel_id, data, status, titulo, conteudo, criador_id
                                        FROM ocorrencias
                                        WHERE status = %s
                                        ORDER BY data_status_alterado DESC, data DESC;
                                    """
                                    params = (status,)

                            cursor.execute(query, params)
                            ocorrencias = cursor.fetchall()

                            if not ocorrencias:
                                ui.notify(f"Nenhum resultado encontrado para '{titulo}'.", type="negative")
                                return

                            # chama a funcao para recarregar
                            refresh_lista_ocorrencias = refreshable_ocorrencias_lista(ocorrencias)

                        finally:
                            cursor.close()
                            conn.close()

                # Botão de Fechar rodapé
                with ui.row().style("position: sticky; bottom: 0; background-color: #008B8B; z-index: 1; padding: 4px 0 8px 0;").classes("w-full justify-center"):
                    ui.button("Fechar", on_click=dialog.close).style(
                        "color: black !important; font-weight: bold; background-color: #fff8ff !important;"
                    ).classes("text-white font-bold px-4 py-2")


        dialog.open()

# ------------------------------------------------- CHAMA O DETALHE DAS OCORRENCIAS ------------------------------------------------

def detalhes_ocorrencia(ocorrencia):
    from Programa_NiceGui.paginas.notificacoes_servicos.notificacoes import mostra_confirmacao
    import Programa_NiceGui.paginas.interface_layout.global_state as global_state

    ocorrencia_id, cliente, num_processo, responsavel, responsavel_id, data_ocorrencia, status, titulo, conteudo_ocorrencia, criador_id = ocorrencia

    global_state.cliente_label = cliente
    global_state.num_processo_label = num_processo
    global_state.titulo_label = titulo
    global_state.conteudo_label = conteudo_ocorrencia

    current_user_id = int(app.storage.user.get("userid"))
    type_user = app.storage.user.get("type_user")
    responsavel_id = int(responsavel_id) if responsavel_id is not None else None

    detalhe_dialog = ui.dialog()

    with detalhe_dialog:
        with ui.card().style('background: #ececf5 !important; width: 480px; height: 440px;').classes("mx-auto"):
            ui.label("Detalhes da Ocorrência").style("font-size: 1.25rem; margin: 0 auto; display: block;").classes(
                "font-bold q-mb-sm")

            print("Responsável ID:", responsavel_id)
            print("User logado ID:", current_user_id)
            print("Status atual:", status)
            print("user logado:", type_user)

            # --------- SELECT de status (só se o user for o responsável) ---------
            if responsavel_id == current_user_id and status in ["Em execução", "Em espera"]:

                with ui.row().classes("items-center q-mb-md"):
                    ui.label("Atualizar Status:").classes("font-bold")

                    status_selecionado = ui.select(
                        options=["", "Em Execução", "Em Espera", "Devolvida", "Concluída", "Cancelada"],
                        value=""
                    ).style("background-color: white; min-width: 160px;").props("outlined dense")


            # Se for admin, é possível atribuir a tarefa (CODIGO DE ATRIBUIR OCORRENCIA)


            responsavel_select = None

            if type_user == 'admin' and status in ["Não atribuída", "Devolvida", "Expirada"]:
                with ui.row().classes("items-center q-mb-md").style("justify-content: space-between; gap: 0.5rem;"):
                    ui.label("Atribuir tarefa:").style("min-width: 110px; margin-right: 8px;").classes("font-bold")

                    usuarios = utilizador_ativo()

                    opcoes_usuarios = {None: 'Selecione...'}
                    opcoes_usuarios.update({u['value']: u['label'] for u in usuarios})
                    responsavel_select = ui.select(
                        options=opcoes_usuarios,
                        value=None
                    ).style("flex: 1; min-width: 140px; max-width: 180px; background-color: white;").props(
                        "outlined dense")

                    ui.button("Atribuir", on_click=lambda: (
                        confirma_atribuicao(ocorrencia_id, responsavel_select.value, detalhe_dialog)
                        if responsavel_select.value else ui.notify("Por favor, selecione um responsável!",type="warning")
                    )).style("color: white; font-weight: bold; background-color: #008B8B !important; min-width: 100px; margin-left: 16px;").classes(
                        "bg-blue-700 text-white font-bold px-4 py-2")



            # Área com rolagem para os dados da ocorrência
            with ui.column().style(
                    "max-height: 300px; overflow-y: auto; overflow-x: hidden; padding-right: 8px; width: 100%; box-sizing: border-box;"
            ).classes("q-mb-sm"):

                if isinstance(data_ocorrencia, str):
                    data_ocorrencia = datetime.strptime(data_ocorrencia, "%Y-%m-%d %H:%M:%S")
                data_formatada = data_ocorrencia.strftime('%d-%m-%Y')

                for titulo_info, valor in [
                    ("Cliente", global_state.cliente_label),
                    ("Nº Processo", global_state.num_processo_label),
                    ("Data", data_formatada),
                    ("Título", global_state.titulo_label),
                ]:
                    with ui.row():
                        ui.label(f"{titulo_info}:").classes("font-bold")
                        ui.label(valor)

                with ui.row():
                    ui.label("Detalhes:").classes("font-bold")
                with ui.row():
                    ui.label(global_state.conteudo_label).style(
                        "text-align: justify; white-space: pre-wrap; width: 100%;"
                    ).classes("text-base")

            # Botões de ação
            with ui.row().classes("w-full flex justify-center items-center q-mt-md gap-4"):
                ui.button("Fechar", on_click=detalhe_dialog.close).style(
                    "color: white; font-weight: bold; background-color: #0a0476 !important;"
                ).classes("bg-green-700 text-white font-bold px-4 py-2 w-32 text-center")

                if responsavel_id == current_user_id and status in ["Em execução", "Em espera"]:
                    ui.button("Confirmar", on_click=lambda: (
                        confirmar_alteracao_status(ocorrencia_id, status_selecionado.value, detalhe_dialog)
                        if status_selecionado.value else ui.notify(
                            "Por favor, selecione um status válido!", type="warning"))
                              ).style("color: white; font-weight: bold; background-color: #008B8B !important;"
                                      ).classes("bg-green-700 text-white font-bold px-4 py-2 w-32 text-center")

                # Botão editar para quem cria a ocorrencia e para os adm
                if (criador_id is not None and current_user_id == criador_id or type_user == 'admin') and status not in ["Concluída"]:
                    ui.button("Editar", on_click=lambda o=ocorrencia: abrir_formulario_edicao(o)).style(
                        "color: white; font-weight: bold; background-color: #dd932a !important;"
                    ).classes("bg-blue-700 text-white font-bold px-4 py-2 w-32 text-center")

                # Botão "Restaurar" visível só para admin nas ocorrências canceladas
                if status == "Cancelada" and app.storage.user.get("type_user") == "admin":
                    ui.button("Restaurar", on_click=lambda: confirmar_restauracao(ocorrencia_id, detalhe_dialog)
                              ).style("color: white; font-weight: bold; background-color: #F2522E !important;"
                                      ).classes("bg-green-700 text-white font-bold px-4 py-2 w-32 text-center")

                # Botão "Aceitar" se a ocorrência estiver devolvida/expirada e sem responsável
                if (status in ["Devolvida", "Expirada"] or responsavel is None) and responsavel_id is None:
                    if current_user_id:
                        ui.button("Aceitar", on_click=lambda o_id=ocorrencia_id, u_id=current_user_id:
                        mostra_confirmacao(o_id, u_id, detalhe_dialog)
                                  ).style("color: white; font-weight: bold; background-color: #008B8B !important;"
                                          ).classes("bg-blue-700 text-white font-bold px-4 py-2 w-32 text-center")

                # Botão "Excluir" visível só para admin nas ocorrências
                if (status in ["Expirada", "Em espera", "Em execução", "Concluída", "Devolvida",
                               "Não atribuída", "Cancelada", "Expirada"] and app.storage.user.get("type_user") == "admin"):
                    ui.button("Excluir", on_click=lambda: confirmar_excluir_ocorrencia(ocorrencia_id, detalhe_dialog)
                              ).style("color: white; font-weight: bold; background-color: #E73B3B !important;"
                                      ).classes("bg-green-700 text-white font-bold px-4 py-2 w-32 text-center")

    detalhe_dialog.open()


# ---------------------------- Funções específicas chamando a função genérica -------------------------------------

def ocorrencia_concluida():
    ocorrencias_filtradas("Concluída", "Ocorrências concluídas")

def ocorrencia_execucao():
    ocorrencias_filtradas("Em Execução", "Ocorrências em execução")

def ocorrencia_espera():
    ocorrencias_filtradas("Em Espera", "Ocorrências em espera")

def ocorrencia_devolvida():
    ocorrencias_filtradas("Devolvida", "Ocorrências devolvidas")

def ocorrencia_expirada_filtro():
    ocorrencias_filtradas("Expirada", "Ocorrências expirada")

def ocorrencia_cancelada():
    ocorrencias_filtradas("Cancelada", "Canceladas")

def nao_atribuida():
    ocorrencias_filtradas("", "Ocorrências não atribuídas", "responsavel IS NULL")

