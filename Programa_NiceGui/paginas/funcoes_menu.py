from Programa_NiceGui.paginas.db_conection import get_db_connection
from nicegui import ui


#CRIAR ROTA NO MAIN



# --------------------------------- EXIBE AS NOTIFICACOES ---------------------------
notificacoes = []

def exibir_notificacoes():
    with ui.dialog() as dialog:
        ui.label("Notificações:").classes("text-h6")

        for mensagem in notificacoes:
            ui.label(mensagem).classes("q-pa-sm")

            ui.button("Fechar", on_click=dialog.close).classes("text-h6 text-primary").props("flat")

# ---------------------------------- ADICIONA UMA NOCA NOTA AO DICIONARIO ------------------------------------

def add_notificacao(mensagem):
    notificacoes.append(mensagem)

# ------------------------------------------- ENVIA AS NOTIFICACOES --------------------------------------

def enviar_notificacao(usuario_id, mensagem):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "INSERT INTO notificacoes (usuario_id, mensagem) VALUES (%s, %s)"
        cursor.execute(query, (usuario_id, mensagem))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def carregar_notificacoes(usuario_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "SELECT mensagem, data_notificacao FROM notificacoes WHERE usuario_id = %s ORDER BY data_notificacao DESC"
        cursor.execute(query, (usuario_id,))
        notificacoes = cursor.fetchall()

        dados_tabela = []

        for notificacao in notificacoes:
            mensagem, data_notificacao = notificacao
            dados_tabela.append({
                "mensagem": mensagem,
                "data_notificacao": data_notificacao
            })
        return dados_tabela

    finally:
        cursor.close()
        conn.close()
