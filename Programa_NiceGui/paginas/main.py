from nicegui import ui
from Programa_NiceGui.paginas.interface_formulario import novo_formulario
from interface_principal import main_page
from Programa_NiceGui.paginas import interface_recuperar_senha
from interface_login_cadastro import login_page, registro_page

from flask import Flask, request, jsonify
from db_conection import get_db_connection
from

# ---------------------------------------------- Configuração das Rotas --------------------------------------------

app = Flask(__name__)

@app.route('/atualizar_status', methods=['POST'])
def atualizar_status():
    dados = request.json
    id_ = dados.get("id")
    novo_status = dados.get("status")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE ocorrencias SET status = %s WHERE id = %s", (novo_status, id_))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"sucesso": True})
    except Exception as e:
        return jsonify({"sucesso": False, "mensagem": str(e)})

@ui.page("/")
def index():
    login_page()

@ui.page("/registro")
def registro():
    registro_page()

@ui.page("/formulario")
def formulario():
    novo_formulario()

@ui.page("/main")
def main():
    main_page()

@ui.page("/redefinir_senha_page")
def redefinir_senha():
    interface_recuperar_senha.redefinir_senha_page()

@ui.page("/recuperacao_senha")
def recuperacao_senha():
    interface_recuperar_senha.recuperar_senha_page()


# ------------------------------------------------ Inicializa o NiceGUI ---------------------------------------------

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(storage_secret="minha_chave_secreta_aleatoria")
