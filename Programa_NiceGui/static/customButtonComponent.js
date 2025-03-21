class CustomButtonComponent {
    eGui;
    eButton;
    eventListener;

    init() {
        this.eGui = document.createElement('div');
        const eButton = document.createElement('button');
        eButton.className = 'btn-simple';
        eButton.textContent = 'Launch!';
        this.eventListener = () => alert('Software Launched');
        eButton.addEventListener('click', this.eventListener);
        this.eGui.appendChild(eButton);
    }

    getGui() {
        return this.eGui;
    }

    refresh() {
        return true;
    }

    destroy() {
        if (this.eButton) {
            this.eButton.removeEventListener('click', this.eventListener);
        }
    }
}

class CustomButtonComponent {
    init(params) {
        this.eGui = document.createElement("div");
        this.eGui.innerHTML = `<button onclick="aceitarOcorrencia(${params.data.id})">Aceitar</button>`;
    }
    getGui() {
        return this.eGui;
    }
}
