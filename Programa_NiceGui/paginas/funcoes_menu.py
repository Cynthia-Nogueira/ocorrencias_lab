
from Programa_NiceGui.paginas.db_conection import get_db_connection
from nicegui import ui, app


#CRIAR ROTA NO MAIN


# --------------------------------- EXIBE AS NOTIFICACOES ---------------------------

notificacoes = []

def exibir_notificacoes():
    global notificacoes
    current_user_id = app.storage.user.get("userid", None)
    notificacoes, _ = carregar_notificacoes(current_user_id)

    with ui.dialog() as dialog:
        ui.label("Notificações:").classes("text-h6")

        for notificacao in notificacoes:
            if not notificacao["lida"]:
                ui.button(notificacao['mensagem'], on_click=lambda id=notificacao['id']: visualizar_notificacao(id)).classes("q-pa-sm")
            else:
                ui.label(notificacao['mensagem']).classes("q-pa-sm")



        ui.button("Fechar", on_click=dialog.close).classes("text-h6 text-primary").props("flat")


# ---------------------------------- ADICIONA UMA NOCA NOTA AO DICIONARIO ------------------------------------

def add_notificacao(mensagem):
    notificacoes.append(mensagem)

# ------------------------------------------- ENVIA AS NOTIFICACOES --------------------------------------

def enviar_notificacao(usuario_id, mensagem):
    conn = get_db_connection()
    if conn is None:                                                    #teste apagar
        raise ValueError("Conexão com o banco de dados falhou.")        #teste apagar
    cursor = conn.cursor()

    try:
        query = "INSERT INTO notificacoes (usuario_id, mensagem, data_notificacao) VALUES (%s, %s, NOW())"
        cursor.execute(query, (usuario_id, mensagem))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

# ------------------------------------------- CARREGA AS NOTIFICACOES --------------------------------------


def carregar_notificacoes(usuario_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "SELECT id, mensagem, data_notificacao, lida FROM notificacoes WHERE usuario_id = %s ORDER BY data_notificacao DESC"
        cursor.execute(query, (usuario_id,))
        notificacoes = cursor.fetchall()

        dados_tabela = []
        notificacoes_nao_lidas = 0

        for notificacao in notificacoes:
            id, mensagem, data_notificacao, lida = notificacao
            if not lida:
                notificacoes_nao_lidas += 1
                dados_tabela.append({
                    "id": id,
                    "mensagem": mensagem,
                    "data_notificacao": data_notificacao,
                    "lida": lida
            })
        return dados_tabela, notificacoes_nao_lidas

    finally:
        cursor.close()
        conn.close()


# -------------------------------- MARCA COMO LIDAS E ATUALIZA NO BD AS NOTIFICACOES --------------------------

def visualizar_notificacao(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "UPDATE notificacoes SET lida = TRUE WHERE id = %s"
        cursor.execute(query, (id,))
        conn.commit()

        # Exibir conteúdo completo da notificação
        query = "SELECT mensagem FROM notificacoes WHERE id = %s"
        cursor.execute(query, (id,))
        mensagem = cursor.fetchone()

        with ui.dialog() as dialog:
            ui.label(mensagem[0]).classes("text-h6 q-pa-md")

            ui.button("Fechar", on_click=dialog.close)

        dialog.open()

    finally:
        cursor.close()
        conn.close()