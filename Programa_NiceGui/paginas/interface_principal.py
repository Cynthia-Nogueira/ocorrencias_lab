
from nicegui import app, ui

#pagina principal
def main_page():
        app.add_static_files('/static', '../static')
        ui.add_head_html('<link rel="stylesheet" type="text/css" href="/static/styles.css">')

        with ui.row().classes('w-full justify-center pt-10'):
                ui.label("Ocorrências Registadas").classes('text-center text-4xl font-bold')



ui.run()