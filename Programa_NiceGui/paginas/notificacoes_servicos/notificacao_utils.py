from nicegui import ui
from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection
from Programa_NiceGui.paginas.notificacoes_servicos.helper_notificacoes import minha_funcao_visualizar_notificacao


def carregar_notificacoes(usuario_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "SELECT id, mensagem, data_notificacao, lida, ocorrencia_id FROM notificacoes WHERE usuario_id = %s ORDER BY data_notificacao DESC"
        cursor.execute(query, (usuario_id,))
        notificacoes_db = cursor.fetchall()

        dados_tabela = []
        notificacoes_nao_lidas = 0

        for notificacao in notificacoes_db:
            id, mensagem, data_notificacao, lida = notificacao
            if not lida:
                notificacoes_nao_lidas += 1
            dados_tabela.append({
                "id": id,
                "mensagem": mensagem,
                "data_notificacao": data_notificacao,
                "lida": lida
            })

        return dados_tabela, notificacoes_nao_lidas  # Retorna notificações e contador de não lidas

    finally:
        cursor.close()
        conn.close()

def enviar_notificacao(usuario_id, mensagem, ocorrencia_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
            INSERT INTO notificacoes (usuario_id, mensagem, data_notificacao, ocorrencia_id)
            VALUES (%s, %s, NOW(), %s)
        """
        cursor.execute(query, (usuario_id, mensagem, ocorrencia_id))
        conn.commit()

    except Exception as e:
        ui.notify(f"Erro ao enviar notificação: {str(e)}", type="negative")

    finally:
        cursor.close()
        conn.close()


# -------------------------------- ATUALIZA INTERFACE NOTIFICACOES --------------------------


def atualiza_interface_notficacoes():
    global notificacoes
    with ui.column().classes("w-full"):
        for notificacao in notificacoes:
            if not notificacao["lida"]:
                ui.button(
                    notificacao["mensagem"],
                    on_click=lambda id=notificacao["id"]: minha_funcao_visualizar_notificacao(id)).style("color: gray; font-weight: "
                                    "bold; background-color: #D7EDE1 !important;").classes("q-pa-sm text-left full-width")
            else:
                ui.label(f"{notificacao['mensagem']}").classes("q-pa-sm text-gray-500").style("background-color: #d2e9dd "
                                                                   "!important; border-radius: 8px; padding: 8px;")



# ---------------------------------- ADICIONA UMA NOCA NOTIFICACAO AO DICIONARIO -------------------------------

def add_notificacao(usuario_id, mensagem):
    enviar_notificacao(usuario_id, mensagem)  # Insere no banco
    notificacoes.append({
        "id": len(notificacoes) + 1,  # Pode ser ajustado para pegar do banco
        "mensagem": mensagem,
        "data_notificacao": None,  # Pode ser ajustada para a data atual com datetime.
        "lida": False
    })


