import smtplib
from email.message import EmailMessage
from email.utils import formataddr

from nicegui import ui


def sendmail(dest: str, token: str) -> None:
    if '@' not in dest or '.' not in dest:
        raise ValueError("Endereço de e-mail do destinatário inválido.")

    sender = "it_bots@iep.pt"
    subject = "Token para redefinição de senha"
    body = f"""Olá,

Aqui está o seu token para redefinir a senha: {token}

Esse token expira em 5 minutos.

Atenciosamente,
Equipe de Suporte
"""


    msg = EmailMessage()
    msg['From'] = formataddr(("Equipe de Suporte", sender))
    msg['To'] = dest
    msg['Subject'] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP('webmail.iep.pt', 25) as smtp:
            smtp.send_message(msg)
            print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        raise

