function statusRenderer(params) {
    const_id = params.data.id;
    const_currentStatus = params.value;

    const_select = document.createElement("select");
    select.classList.add("status-select");

    const_statuses = ["Em espera", "Em execução", "Concluído"];
    statuses.forEach(status => {
        const option = document.createElement("option");
        option.value = status;
        option.textContent = status;
        if (status === currentStatus) {
            option.selected = true;
        }
        select.appendChild(option);
    });

    select.addEventListener("change", function () {
        fetch('/atualizar_status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: id, status: this.value })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log("Status atualizado com sucesso!");
            } else {
                console.error("Erro ao atualizar status:", data.error);
            }
        })
        .catch(error => console.error("Erro na requisição:", error));
    });

    return select;
}

