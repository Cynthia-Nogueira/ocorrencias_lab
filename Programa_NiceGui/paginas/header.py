from nicegui import ui

from nicegui import ui

def pag_layout():
    # Right Drawer (Menu lateral)
    with ui.right_drawer(fixed=False).style('background-color: #DCF5ED').props('bordered') as right_drawer:
        ui.label('MENU')
        ui.button('Página Inicial', on_click=lambda: ui.navigate('/')).props('flat')
        ui.button('Formulário', on_click=lambda: ui.navigate('/formulario')).props('flat')
        ui.button('Login', on_click=lambda: ui.navigate('/login')).props('flat')
        ui.button('Registro', on_click=lambda: ui.navigate('/registro')).props('flat')

    # Cabeçalho (Header)
    with ui.header(elevated=True).style('background-color: #009696').classes('items-center justify-between'):
        ui.label('HEADER').classes('mx-auto')
        ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=white')

# Chama a função para rodar o app
ui.run()

