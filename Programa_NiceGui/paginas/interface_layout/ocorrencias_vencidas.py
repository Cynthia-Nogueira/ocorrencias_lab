import holidays
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from Programa_NiceGui.paginas.banco_dados.db_conection import get_db_connection

#-------------------------------------------- VERIFICA OCORRENCIAS EXPIRADAS --------------------------------------------



# FAZER TESTES PARA VER SE ESTA FUNCIONANDO



def ocorrencias_expiradas():
    print("[SCHEDULER] Verificando ocorrências expiradas...")

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT id, data_aceite
    FROM ocorrencias
    WHERE status = 'Em espera' AND data_aceite IS NOT NULL
    """
    cursor.execute(query)
    ocorrencias = cursor.fetchall()

    agora = datetime.now()
    feriados = feriados_portugal()

    for id_ocorrencia, data_aceite in ocorrencias:
        if isinstance(data_aceite, str):
            try:
                data_aceite = datetime.strptime(data_aceite, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                data_aceite = datetime.strptime(data_aceite, "%Y-%m-%d")

        total_horas = horas_uteis(data_aceite, agora, feriados)

        # Convertendo o timedelta para horas
        total_horas_em_horas = total_horas.total_seconds() / 3600

        if total_horas_em_horas >= 48:
            print(f"[INFO] Ocorrência {id_ocorrencia} devolvida!")                #APAGAR
            cursor.execute("""
                   UPDATE ocorrencias
                   SET status = 'Devolvida', responsavel_id = NULL, data_aceite = NULL
                   WHERE id = %s
               """, (id_ocorrencia,))
            conn.commit()

    cursor.close()
    conn.close()

# -------------------------------------- CARREGA O PROGRAMA A CADA X HORAS --------------------------------------------

def inicia_verificacao():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(ocorrencias_expiradas, 'interval', seconds=20)  # TROCAR O TEMPO PARA TESTAR, DEPOIS QUE TODOS OS BOTOES FUNCIONAR
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
    horas_totais = timedelta()
    while data_inicio < data_fim:
        if data_inicio.weekday() < 5 and not is_feriado(data_inicio, feriados):
            horas_totais += timedelta(hours=24)
        data_inicio += timedelta(days=1)

    # subtraindo o tempo restante do último dia
    horas_restantes = timedelta(seconds=(data_fim - data_inicio).total_seconds())
    horas_totais -= horas_restantes
    return horas_totais
