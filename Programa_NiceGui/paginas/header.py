from nicegui import ui

#cabeçalho da pagina
def header():
    with ui.row().classes("w-full items-center"):
        result = ui.label().classes("mr-auto")
        with ui.button(on_click=lambda: menu.open()).props('icon="menu"').style("color=#008B8B"):
            with ui.menu() as menu:
                ui.menu_item('Menu item 1', lambda: result.set_text('Selected item 1'))
                ui.menu_item('Menu item 2', lambda: result.set_text('Selected item 2'))
                ui.menu_item('Menu item 3', lambda: result.set_text('Selected item 3'))
                ui.menu_item('Menu item 4(keep open)', lambda: result.set_text('Selected item 4'), auto_close=False)
                ui.separator()
                ui.menu_item('Close', on_click=menu.close)



