from nicegui import ui
from nicegui.elements import grid
import Programa_NiceGui.paginas.interface_layout.global_state as global_state
from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection, obter_dados
from Programa_NiceGui.paginas.notificacoes_servicos.notificacao_utils import enviar_notificacao, carregar_notificacoes
from Programa_NiceGui.paginas.notificacoes_servicos.ocorrencias import obter_ocorrencias

# --------------------------------------------------- CARREGA A TABELA ---------------------------------------

def carregar_tabela(grid, usuario_logado):
    dados_tabela = []

    try:
        for ocorrencia in obter_ocorrencias():
            id_, cliente, num_processo, data, status, conteudo, responsavel = ocorrencia

            # Convertendo a ocorrência para dicionário (evita erro JSON serializable)
            dados_tabela.append({
                "id": id_,
                "cliente": cliente,
                "num_processo": num_processo,
                "data": data,
                "status": status,
                "conteudo": conteudo,
                "responsavel": responsavel or "Responsável vazio",
                "acoes": "Botão aqui"  # PlaceHolder (pois UI não pode ser passado para AgGrid)
            })

        # Atualiza a tabela com os dados convertidos corretamente
        atualizar_tabela(grid, dados_tabela)

    except Exception as e:
        ui.notify(f"Erro ao carregar a tabela: {e}", color="red")

    global_state.grid = grid


# ------------------------------------------- ATUALIZA A TABELA -------------------------------------------


def atualizar_tabela(grid, dados_tabela):
    # Atualiza os dados na tabela
    grid.options["rowData"] = dados_tabela
    grid.update()

# --------------------------------- ACEITA A TARREFA ------------------------------

# Variável global para controlar a execução de carregar_tabela

tabela_recarregada = False

def aceitar_ocorrencia(ocorrencia_id, usuario_id, detalhe_dialog):
    global tabela_recarregada

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Obtém informações do usuário que aceitou
        cursor.execute("SELECT CONCAT(nome, ' ', apelido) AS nome_completo FROM utilizador WHERE id = %s", (usuario_id,))
        usuario = cursor.fetchone()
        if not usuario:
            ui.notify("Erro: Usuário não encontrado.", type="negative")
            return

        nome_completo = usuario['nome_completo']  # Nome completo do usuário

        # Obtém informações da ocorrência
        cursor.execute("SELECT cliente, num_processo, status FROM ocorrencias WHERE id = %s", (ocorrencia_id,))
        ocorrencia = cursor.fetchone()
        if not ocorrencia:
            ui.notify("Erro: Ocorrência não encontrada.", type="negative")
            return

        cliente, num_processo, status = ocorrencia

        # Atualiza o status da ocorrência para "Em execução" e atribui o responsável
        query = "UPDATE ocorrencias SET status = 'Em execução', responsavel = %s WHERE id = %s"
        cursor.execute(query, (nome_completo, ocorrencia_id))
        conn.commit()

        # Busca todos os usuários, menos quem aceitou
        cursor.execute("SELECT id FROM utilizador WHERE id != %s", (usuario_id,))
        outros_usuarios = cursor.fetchall()

        # Envia notificação para os demais usuários
        mensagem = f"{nome_completo} aceitou a ocorrência {num_processo} do cliente {cliente}."
        for usuario in outros_usuarios:
            enviar_notificacao(usuario[0], mensagem)

        # Notifica o usuário que aceitou
        ui.notify("Ocorrência aceita com sucesso!", type="success")

        # Atualiza a lista de notificações
        carregar_notificacoes(usuario_id)

        # Evitar o ciclo chamando carregar_tabela apenas uma vez
        if not tabela_recarregada:
            tabela_recarregada = True
            carregar_tabela(global_state.grid, usuario_id)  # Carrega a tabela


    except Exception as e:
        ui.notify(f"Erro ao aceitar ocorrência: {str(e)}", type="negative")

    finally:
        cursor.close()
        conn.close()

    detalhe_dialog.close()

