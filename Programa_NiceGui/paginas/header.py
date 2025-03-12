from nicegui import ui, app
from Programa_NiceGui.paginas.funcoes_menu import notificacoes, exibir_notificacoes, carregar_notificacoes


#---------------------------------------------- INTERFACE DO MENU -----------------------------

def pag_layout():
    current_user_id = app.storage.user.get("userid", None)

    # Right Drawer (Menu lateral a direita)
    with ui.right_drawer(fixed=False).style('background-color: #DCF5ED').props('bordered') as right_drawer:
        ui.label('MENU').style('color: #5898D4; font-weight: bold;').classes('text-h6 mx-auto')

        # Obtém o número de notificações não lidas para o usuário atual
        identif_usuario = current_user_id if current_user_id is not None else None
        notificacoes, notificacoes_nao_lidas = ([], 0) if identif_usuario is None else carregar_notificacoes(identif_usuario)

        # icone de notificacoes no menu
        if notificacoes_nao_lidas > 0:
            ui.button(f"Notificações ({notificacoes_nao_lidas})", icon="notifications", on_click=exibir_notificacoes).style('color: red;').props('flat')
        else:
            ui.button('Notificações', icon='notifications', on_click=exibir_notificacoes).props('flat')

        #vem campo com as ocorrencias em aberto
        #vem campo com as ocorrencias em em execucao
        #vem campo com as ocorrencias em concluidas

    # Cabeçalho (Header)
    with ui.header(elevated=True).style('background-color: #009696').classes('items-center justify-between'):
        ui.label('Colocar logo à equerda')
        ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=white')


        #PRECISA????

        # Botão para adicionar notificações (simula a criação de uma nova notificação)
        #ui.button('Adicionar Notificação', on_click=lambda: adicionar_notificacao('Nova notificação de teste!')).props(
         #   'flat color=blue')

# Chama a função para rodar o app
ui.run()