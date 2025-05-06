from nicegui import ui, app
from Programa_NiceGui.paginas.interface_layout.formulario import novo_formulario
from Programa_NiceGui.paginas.notificacoes_servicos.interface_principal import main_page
from Programa_NiceGui.paginas.notificacoes_servicos import recuperar_senha
from Programa_NiceGui.paginas.interface_layout.auth import login_page, registro_page, pagina_protegida
from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection
from Programa_NiceGui.paginas.interface_layout.header import pag_layout
from Programa_NiceGui.paginas.interface_layout.page_user import carregar_ocorrencias_user
from Programa_NiceGui.paginas.interface_layout.ocorrencias_vencidas import inicia_verificacao

# ---------------------------------------------- Configuração das Rotas --------------------------------------------

@app.post('/atualizar_status')
async def atualizar_status(request: dict):
    id_ = request.get("id")
    novo_status = request.get("status")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE ocorrencias SET status = %s WHERE id = %s", (novo_status, id_))
        conn.commit()
        cursor.close()
        conn.close()
        return {"sucesso": True}
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


@ui.page("/")
def index():
    login_page()

@app.on_startup
async def startup():
    inicia_verificacao()

@ui.page("/registro")
def registro():
    registro_page()

@ui.page("/formulario")
def formulario():
    novo_formulario()

@ui.page("/main")
def main():
    if not pagina_protegida(): return
    pag_layout()
    main_page()

@ui.page("/redefinir_senha_page")
def redefinir_senha():
    recuperar_senha.redefinir_senha_page()

@ui.page("/recuperacao_senha")
def recuperacao_senha():
    recuperar_senha.recuperar_senha_page()

@ui.page("/page_user")
def page_user():
    pag_layout()
    carregar_ocorrencias_user()

# ------------------------------------------------ Inicializa o NiceGUI ---------------------------------------------

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(storage_secret="minha_chave_secreta_aleatoria")

