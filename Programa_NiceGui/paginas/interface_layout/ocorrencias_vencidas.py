import holidays
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection
from Programa_NiceGui.paginas.notificacoes_servicos.notificacao_utils import enviar_notificacao
from Programa_NiceGui.paginas.notificacoes_servicos.utilizadores import obter_lista_user


#-------------------------------------------- VERIFICA OCORRENCIAS EXPIRADAS --------------------------------------------

def ocorrencias_expiradas(modo_teste=False):
    print("[SCHEDULER] Verificando ocorrências expiradas...")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:

        # Busca ocorrências em "Em Espera" com data de aceite
        query = """
        SELECT id, data_aceite
        FROM ocorrencias
        WHERE status = 'Em espera' AND data_aceite IS NOT NULL
        ORDER BY data_status_alterado DESC, data DESC;
        """

        cursor.execute(query)
        ocorrencias = cursor.fetchall()

        agora = datetime.now()
        feriados = feriados_portugal()

        for id_ocorrencia, data_aceite in ocorrencias:
            # Converte string para datetime se necessário
            if isinstance(data_aceite, str):
                try:
                    data_aceite = datetime.strptime(data_aceite, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    data_aceite = datetime.strptime(data_aceite, "%Y-%m-%d")

            # Calcula o tempo passado
            total_horas = horas_uteis(data_aceite, agora, feriados)
            total_segundos = total_horas.total_seconds()
            total_horas_em_horas = total_segundos / 3600

            # Define limite com base no modo de teste ou não
            limite_segundos = 30 if modo_teste else 48 * 3600

            print(f"[DEBUG] Ocorrência {id_ocorrencia}: {total_horas_em_horas:.2f}h desde aceite | Limite: {limite_segundos / 3600:.2f}h")

            if total_segundos >= limite_segundos:
                print(f"[EXPIRADA] Ocorrência {id_ocorrencia} atingiu o limite!")
                # Busca o título e o responsável atual da ocorrência
                cursor.execute("SELECT titulo, responsavel_id FROM ocorrencias WHERE id = %s", (id_ocorrencia,))
                resultado = cursor.fetchone()
                titulo = resultado[0] if resultado else "Sem título"
                responsavel_id = resultado[1] if resultado else None


                # Atualiza o status da ocorrência para "Expirada" e limpa os campos relacionados
                cursor.execute("""
                    UPDATE ocorrencias
                    SET status = 'Expirada', responsavel_id = NULL, data_aceite = NULL
                    WHERE id = %s
                """, (id_ocorrencia,))
                conn.commit()

                # Envia notificação de expiração para todos os usuários
                cursor.execute("SELECT id FROM utilizador")
                usuarios = cursor.fetchall()

                for (usuario_id,) in usuarios:
                    mensagem = f"⏳ A ocorrência '{titulo}' foi devolvida automaticamente. Prazo expirado!"
                    enviar_notificacao(usuario_id, mensagem, id_ocorrencia, tipo_ocorrencia="Expirada")

    except Exception as e:
        print(f"[ERRO] Falha ao verificar ocorrências expiradas: {e}")

    finally:
        cursor.close()
        conn.close()

# -------------------------------------- CARREGA O PROGRAMA A CADA X HORAS --------------------------------------------

def inicia_verificacao():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(ocorrencias_expiradas, 'interval', hours=3)
    scheduler.start()
# ---------------------------------------------- FERIADOS PORTUGAL -------------------------------------------------

def feriados_portugal():
    ano_atual = datetime.now().year
    feriados = holidays.Portugal(years=ano_atual)
    return {feriado for feriado in feriados.keys()}

# ----------------------------------------- VERIFICA SE É FERIADO -------------------------------------------------

def is_feriado(data, feriados):
    return data.date() in feriados

# ----------------------------------------- CALCULA AS HORAS --------------------------------------------

def horas_uteis(data_inicio, data_fim, feriados):
    horas = 0
    atual = data_inicio

    while atual < data_fim:
        if atual.weekday() < 5 and atual.date() not in feriados:
            horas += 1
        atual += timedelta(hours=1)

    return timedelta(hours=horas)
