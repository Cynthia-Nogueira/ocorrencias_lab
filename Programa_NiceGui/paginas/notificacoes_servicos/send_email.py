import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#--------------------------------------------- ENVIA EMAIL PARA RECUPERAR SENHA ----------------------------------------

# Função para enviar o e-mail
def sendmail(email):
    remetente = "it_bots@iep.pt"
    destinatario = email

    # Corpo do e-mail
    assunto = "Link: redefinir senha"
    corpo = """
    Olá,

    Clique no link abaixo para redefinir sua senha:
    http://127.0.0.1:8080/redefinir_senha_page

    Atenciosamente,
    Equipe Suporte
    """

    # Criação da mensagem
    mensagem = MIMEMultipart()
    mensagem['From'] = remetente
    mensagem['To'] = destinatario
    mensagem['Subject'] = assunto

    # Corpo do e-mail como texto
    mensagem.attach(MIMEText(corpo, 'plain'))

    try:
        # servidor SMTP local
        servidor = smtplib.SMTP('webmail.iep.pt', 25)
        servidor.sendmail(remetente, destinatario, mensagem.as_string())  # envia o e-mail
        servidor.quit()

        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

