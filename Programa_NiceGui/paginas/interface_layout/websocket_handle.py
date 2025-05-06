import json
from socket import socket
from Programa_NiceGui.paginas.interface_layout.menu import detalhes_ocorrencia

# -------------------------------- AJUDA NOS FILTROS DOS QUADROS DE USER E MAIN ---------------------------------

# Handler para o evento de clique vindo do JavaScript
def handle_socket_messages():
    @socket.on_message
    async def handle_message(msg):
        data = json.loads(msg)
        if data.get('type') == 'cell_clicked':
            # Cria um dicionário para a funcao detalhes_ocorrencia - para o quadro
            ocorrencia_data = (
                data['data'].get('id'),
                data['data'].get('cliente'),
                data['data'].get('num_processo'),
                data['data'].get('responsavel'),
                data['data'].get('responsavel_id'),
                data['data'].get('data'),
                data['data'].get('status'),
                data['data'].get('titulo'),
                data['data'].get('conteudo'),
                data['data'].get('criador_id')
            )
            detalhes_ocorrencia(ocorrencia_data)