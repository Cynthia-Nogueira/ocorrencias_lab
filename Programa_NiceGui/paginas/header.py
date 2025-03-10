from nicegui import ui

from Programa_NiceGui.paginas.funcoes_menu import notificacoes, exibir_notificacoes


def pag_layout():
    # Right Drawer (Menu lateral a direita)
    with ui.right_drawer(fixed=False).style('background-color: #DCF5ED').props('bordered') as right_drawer:
        ui.label('MENU')
        ui.button('Página Inicial', on_click=lambda: ui.navigate('/')).props('flat')
        ui.button('Formulário', on_click=lambda: ui.navigate('/formulario')).props('flat')
        ui.button('Login', on_click=lambda: ui.navigate('/login')).props('flat')
        ui.button('Registro', on_click=lambda: ui.navigate('/registro')).props('flat')

        # icone de notificacoes no menu
        if notificacoes:
            ui.button("Notificações", icon="notifications", on_click=exibir_notificacoes).style('color: red;').props('flat')
        else:
            ui.button('Notificações', icon='notifications', on_click=exibir_notificacoes).props('flat')

    # Cabeçalho (Header)
    with ui.header(elevated=True).style('background-color: #009696').classes('items-center justify-between'):
        ui.label('HEADER').classes('mx-auto')
        ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=white')


        #PRECISA????

        # Botão para adicionar notificações (simula a criação de uma nova notificação)
        #ui.button('Adicionar Notificação', on_click=lambda: adicionar_notificacao('Nova notificação de teste!')).props(
         #   'flat color=blue')

# Chama a função para rodar o app
ui.run()