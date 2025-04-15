from datetime import datetime
from nicegui import app


# ---------------------------- EVITA BUG NA VIEW DE NOTIFICACAOES --------------------------------------

def minha_funcao_visualizar_notificacao():
    from Programa_NiceGui.paginas.notificacoes_servicos.notificacoes import visualizar_notificacao
    return visualizar_notificacao()

# ---------------------------------- FORMATANDO DATAS -----------------------------------------


def formatar_data_para_interface(data_raw):
    #FORMATA A DATA
    if not data_raw:
        return "Sem data"

    formatos_possiveis = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d")

    for fmt in formatos_possiveis:
        try:
            return datetime.strptime(str(data_raw), fmt).strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            continue

    return "Sem data"

# ------------------------------------- CHAMA O NOME DO USER -----------------------------------

def atribui_nome_usuario():
    return app.storage.user.get("username") or "Um usuário"