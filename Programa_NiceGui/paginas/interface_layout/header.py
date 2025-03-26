from nicegui import ui, app
from fastapi.responses import RedirectResponse
from Programa_NiceGui.paginas.banco_dados.db_conection import obter_user_logado
from Programa_NiceGui.paginas.interface_layout.menu import carregar_notificacoes, exibir_notificacoes_menu, ocorrencia_execucao, ocorrencia_espera, ocorrencia_concluida


#---------------------------------------------- INTERFACE DO MENU -----------------------------

def pag_layout():
    current_user_id = app.storage.user.get("userid", None)

    if current_user_id is not None:
        name_logado = obter_user_logado(current_user_id)
    else:
        name_logado = "Usuário não identificado"  # Adicionando a lógica para o caso de não encontrar o usuário

    # Right Drawer (Menu lateral a direita)
    with ui.right_drawer(fixed=False).style('background-color: #DCF5ED').props('bordered') as right_drawer:
        ui.label('MENU').style('color: #5898D4; font-weight: bold;').classes('text-h6 mx-auto')

        # Obtém o número de notificações não lidas para o usuário atual
        identif_usuario = current_user_id if current_user_id is not None else None
        notificacoes, notificacoes_nao_lidas = ([], 0) if identif_usuario is None else carregar_notificacoes(identif_usuario)

        # Ícone de notificações no menu
        if notificacoes_nao_lidas > 0:
            ui.button(f"Notificações ({notificacoes_nao_lidas})", icon="notifications", on_click=exibir_notificacoes_menu).props('flat')
        else:
            ui.button('Notificações', icon='notifications', on_click=exibir_notificacoes_menu).props('flat')

        # Botão (em espera)
        ui.button("Ocorrências Em espera", icon='arrow_right', on_click=ocorrencia_espera).props('flat')

        # Botão (em execução)
        ui.button("Ocorrências Em Execução", icon='arrow_right', on_click=ocorrencia_execucao).props('flat')

        # Botão (concluído)
        ui.button("Ocorrências Concluídas", icon='arrow_right', on_click=ocorrencia_concluida).props('flat')

        # Botão de logout no menu
        ui.button("Sair", icon="logout", on_click=logout).props('flat')

    # Cabeçalho (Header)
    with ui.header(elevated=True).style('background-color: #009696').classes('items-center justify-between'):
        ui.label('Colocar logo à esquerda').style('color: white; font-size: 20px; font-weight: bold;')
        #ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=white')

        # Ícone de menu e nome do usuário logado
        with ui.row().classes('items-center gap-x-4'):
            ui.label(name_logado).style('color: white; font-size: 16px;')
            ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=white')



# ------------------------------------- DESCONECTA DA PAGINA -----------------------------------------

# Função para logout
# Função para logout
def logout():
    # Limpar os dados específicos de usuário armazenados
    if 'user' in app.storage:
        del app.storage['user']

    # Limpar também o nome do usuário, se necessário
    if 'name_logado' in app.storage:
        del app.storage['name_logado']

    # Redireciona para a página de login
    return RedirectResponse(url='/login')

# ------------------------------------- RODA O APP (N FUNCIONA SEM) -----------------------------------------


# Chama a função para rodar o app
ui.run(storage_secret="minha_chave_secreta_aleatoria")





