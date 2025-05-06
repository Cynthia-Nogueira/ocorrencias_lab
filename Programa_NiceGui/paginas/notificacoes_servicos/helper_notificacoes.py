from nicegui import app

# ---------------------------- EVITA BUG NA VIEW DE NOTIFICACAOES --------------------------------------

def minha_funcao_visualizar_notificacao():
    from Programa_NiceGui.paginas.notificacoes_servicos.notificacoes import visualizar_notificacao
    return visualizar_notificacao()

# ------------------------------------- CHAMA O NOME DO USER -----------------------------------

def atribui_nome_usuario():
    return app.storage.user.get("username") or "Um usuário"