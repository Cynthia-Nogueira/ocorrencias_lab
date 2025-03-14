
#quero deixar nova ocorrencia, nome cliente e n pocesso em negrito.
#o nome de quem regostrou a ocorrencia deve aparecer centralizado


def formatar_mensagem(nome_user, cliente, num_processo):
    return (
        f"• Nova ocorrência registrada por:\n {nome_user}\n"
        f"• Nome do cliente: {cliente}\n"
        f"• Nº Processo: {num_processo}"
    )

"""
Crie a mensagem na função de notificação Reutilize essa função 
no local onde mensagem_notificacao está sendo criada:

mensagem_notificacao = formatar_mensagem(nome_user, cliente.value, num_processo.value)
enviar_notificacao(user['id'], mensagem_notificacao)


mensagem_formatada = mensagem_notificacao.replace("\n", "<br>")  # Substitui quebras de linha para HTML

ui.markdown(f"{mensagem_formatada}").style("color: #40403e;").classes("text-lg q-pa-md")

Código atualizado com reutilização da lógica
Se você quer garantir que a mesma mensagem (conteúdo) seja reutilizada entre os dois blocos, segue o exemplo consolidado:


# Função reutilizável para gerar mensagem
def formatar_mensagem(nome_user, cliente, num_processo):
    return (
        f"• Nova ocorrência registrada por:\n {nome_user}\n"
        f"• Nome do cliente: {cliente}\n"
        f"• Nº Processo: {num_processo}"
    )


# Enviar a notificação para os usuários, excluindo o usuário logado
for user in lista_user:
    if user['id'] != current_user_id:
        # Reutiliza a função para criar uma mensagem
        mensagem_notificacao = formatar_mensagem(nome_user, cliente.value, num_processo.value)

        # Envia a notificação
        enviar_notificacao(user['id'], mensagem_notificacao)

        # Formata a mensagem para exibição no diálogo (usando HTML)
        mensagem_formatada = mensagem_notificacao.replace("\n", "<br>")

        # Mostra a mensagem formatada no diálogo
        with ui.dialog() as detalhe_dialog:
            with ui.card().classes("w-96"):
                ui.label("Detalhes da Notificação").style("color: #40403e;").classes(
                    "text-lg font-bold mx-auto q-mb-md")
                ui.markdown(f"{mensagem_formatada}").style("color: #40403e;").classes("text-lg q-pa-md")
                ui.button("Fechar", on_click=lambda: fechar_notificacao(detalhe_dialog)).style(
                    "color: white !important; font-weight: bold; background-color: #5a7c71 !important;"
                ).classes("text-primary mx-auto").props("flat")




"""