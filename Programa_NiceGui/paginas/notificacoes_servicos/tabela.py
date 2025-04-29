from nicegui import ui
from nicegui.elements import grid
from datetime import datetime, date
import Programa_NiceGui.paginas.interface_layout.global_state as global_state
from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection, obter_dados
from Programa_NiceGui.paginas.notificacoes_servicos.notificacao_utils import enviar_notificacao, carregar_notificacoes
from Programa_NiceGui.paginas.notificacoes_servicos.ocorrencias import obter_ocorrencias, ultima_ocorrencia_id


# --------------------------------------------------- CARREGA A TABELA ---------------------------------------

def carregar_tabela(grid, usuario_logado):
    dados_tabela = []

    try:
        for ocorrencia in obter_ocorrencias():
            id_, cliente, num_processo, responsavel, data, status, titulo, conteudo  = ocorrencia

            # Verifica se a variável 'data' é uma string
            if isinstance(data, str):
                try:
                    data_formatada = datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
                except ValueError:
                    ui.notify(f"Erro ao formatar a data: '{data}' não corresponde ao formato esperado.", color="red")
                    data_formatada = data
            elif isinstance(data, date):
                data_formatada = data.strftime("%d/%m/%Y")
            else:
                # se a data não for string nem datetime trata o erro
                ui.notify(f"Data inválida: {data}", color="red")
                data_formatada = "Data inválida"

            # Convertendo a ocorrência para dicionário (evita erro JSON serializable)
            dados_tabela.append({
                "id": id_,
                "cliente": cliente,
                "num_processo": num_processo,
                "responsavel": responsavel or "Responsável vazio",
                "data": data_formatada,
                "status": status,
                "titulo": titulo,
                "conteudo": conteudo,
                "acoes": "Botão aqui"  # Placeholder (pois UI não pode ser passado para AgGrid)
            })

        # Atualiza a tabela
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

def aceitar_ocorrencia(ocorrencia_id, ultima_usuario_id, detalhe_dialog, confirm_dialog):
    global tabela_recarregada

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Obtém informações do usuário que aceitou
        cursor.execute("SELECT CONCAT(nome, ' ', apelido) AS nome_completo FROM utilizador WHERE id = %s", (ultima_usuario_id,))
        usuario = cursor.fetchone()

        if not usuario:
            ui.notify("Erro: Usuário não encontrado.", type="negative")
            return

        nome_completo = usuario[0]

        # Obtém informações da ocorrência
        cursor.execute("SELECT cliente, titulo, responsavel, status FROM ocorrencias WHERE id = %s", (ocorrencia_id,))
        ocorrencia = cursor.fetchone()

        if not ocorrencia:
            ui.notify("Erro: Ocorrência não encontrada.", type="negative")
            return

        # Dados da ocorrência
        cliente, titulo, responsavel, status = ocorrencia

        # Atualiza o status da ocorrência para "Em execução" e atribui o responsável
        query = """
            UPDATE ocorrencias 
            SET status = 'Em execução', 
                responsavel = %s, 
                responsavel_id = %s,
                data_aceite = %s,
                data_status_alterado = %s
            WHERE id = %s
        """
        cursor.execute(query, (nome_completo, ultima_usuario_id, datetime.now(), datetime.now(), ocorrencia_id))

        conn.commit()

        # Busca todos os usuários, menos quem aceitou
        cursor.execute("SELECT id FROM utilizador WHERE id != %s", (ultima_usuario_id,))
        outros_usuarios = cursor.fetchall()

        # Envia notificação para os demais usuários
        mensagem = f"✅ {nome_completo} aceitou a ocorrência '{titulo}' do cliente {cliente}"

        for usuario in outros_usuarios:
            enviar_notificacao(usuario[0], mensagem, ocorrencia_id, tipo_ocorrencia="Em execução")

        # Notifica o usuário que aceitou
        ui.notify("Ocorrência aceita com sucesso!", color="green")

        # Atualiza a lista de notificações
        carregar_notificacoes(ultima_usuario_id)

        # Evita o ciclo chamando carregar_tabela apenas uma vez
        if not tabela_recarregada:
            tabela_recarregada = True
            carregar_tabela(global_state.grid, ultima_usuario_id)

    except Exception as e:
        ui.notify(f"Erro ao aceitar ocorrência: {str(e)}", type="negative")
        print(f"Detalhes do erro: {e}")

    finally:
        cursor.close()
        conn.close()

    detalhe_dialog.close()


