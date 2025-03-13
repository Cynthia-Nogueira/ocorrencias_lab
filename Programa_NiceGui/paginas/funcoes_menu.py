from Programa_NiceGui.paginas.db_conection import get_db_connection
from nicegui import ui, app


# --------------------------------- EXIBE AS NOTIFICACOES ---------------------------

notificacoes = []   #nao funciona

def exibir_notificacoes():
    global notificacoes
    current_user_id = app.storage.user.get("userid", None)
    #notificacoes, _ = carregar_notificacoes(current_user_id)
    notificacoes, notificacoes_nao_lidas = carregar_notificacoes(current_user_id)

    with ui.dialog() as dialog:
        with ui.card().classes("w-120 mx-auto q-pa-md") as card_notificacoes:
            ui.label("Notificações:").classes("text-2xl mx-auto font-bold mb-4").style("color: black; font-weight: bold;")

            # Aplica estilo no cartão para adicionar scroll e limitar altura
            card_notificacoes.classes("q-pa-md")
            card_notificacoes.style("background-color: #B8B8B8; border-radius: 10px; overflow-y: auto;"
                                    "width: 600px; height: 500px;")

            # Lista de notificações com rolagem
            with ui.column().classes("w-full"):
                for notificacao in notificacoes:
                    if not notificacao["lida"]:
                        ui.button(
                            notificacao["mensagem"],
                            on_click=lambda id=notificacao["id"]: visualizar_notificacao(id)
                        ).classes("q-pa-sm text-left full-width").style(
                            "background-color: #d0d0d0 !important; color: black !important; border: 2px solid #ffffff; border-radius: 8px;"
                        )

                    else:
                        ui.label(f"✅ {notificacao['mensagem']}").classes("q-pa-sm text-gray-500").style(
                            "background-color: #E8E8E8 !importante; border-radius: 8px; padding: 8px;"  # tom mais claro
                        )

            ui.button("Fechar", on_click=dialog.close, color="#878787").classes("btn-primary w-32 mx-auto").style(
                "color: white; font-weight: bold"
            )

    dialog.open()


# -------------------------------- MARCA COMO LIDAS E ATUALIZA NO BD AS NOTIFICACOES --------------------------


#Marca uma notificação como lida, exibe seus detalhes e (opcionalmente) recarrega a lista.

def visualizar_notificacao(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Atualiza no banco de dados para marcar como lida
        query = "UPDATE notificacoes SET lida = TRUE WHERE id = %s"
        cursor.execute(query, (id,))
        conn.commit()

        # Obtém a mensagem da notificação
        query = "SELECT mensagem FROM notificacoes WHERE id = %s"
        cursor.execute(query, (id,))
        mensagem = cursor.fetchone()

        # Exibe o conteúdo completo da notificação em um novo diálogo
        with ui.dialog() as detalhe_dialog:
            with ui.card().classes("w-96"):
                ui.label(mensagem[0]).classes("text-h6 q-pa-md")
                ui.button("Fechar", on_click=lambda: fechar_notificacao(detalhe_dialog)).classes("text-primary").props("flat")

        detalhe_dialog.open()

    finally:
        cursor.close()
        conn.close()

def fechar_notificacao(detalhe_dialog):
    detalhe_dialog.close()



# ---------------------------------- ADICIONA UMA NOCA NOTIFICACAO AO DICIONARIO -------------------------------

def add_notificacao(mensagem):
    notificacoes.append(mensagem)   #rever se funciona tudo

# ------------------------------------------- ENVIA AS NOTIFICACOES --------------------------------------

def enviar_notificacao(usuario_id, mensagem):
    conn = get_db_connection()
    if conn is None:
        raise ValueError("Conexão com o banco de dados falhou.")        #ja funciona
    cursor = conn.cursor()

    try:
        query = "INSERT INTO notificacoes (usuario_id, mensagem, data_notificacao) VALUES (%s, %s, NOW())"
        cursor.execute(query, (usuario_id, mensagem))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

# ------------------------------------------- LISTA COMPLETA DE NOTIFICACOES --------------------------------------


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


