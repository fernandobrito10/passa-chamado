# Guia para Desenvolvimento de Aplicativo Web de Distribuição de Chamados com Agidesk

Este guia detalha os passos para desenvolver um aplicativo web que permita distribuir chamados do Agidesk para técnicos utilizando uma interface intuitiva de arrastar e soltar. 

## Estrutura do Projeto
```
/Projeto
|-- /backend
|   |-- app.py
|   |-- agidesk_api.py
|   |-- config.py
|-- /frontend
|   |-- index.html
|   |-- app.js
|   |-- styles.css
|-- requirements.txt
|-- README.md
```

## 1. Configuração Inicial
Instale as dependências necessárias:

```
pip install flask requests
```

Crie o arquivo `requirements.txt` e adicione as dependências:
```
flask
requests
```

## 2. Backend - Conexão com a API do Agidesk
### `config.py`
```python
API_URL = "https://api.agidesk.com/v1"
API_KEY = "SUA_CHAVE_DE_API"
```

### `agidesk_api.py`
```python
import requests
from config import API_URL, API_KEY

def get_unassigned_tickets():
    response = requests.get(f"{API_URL}/tickets", headers={"Authorization": f"Bearer {API_KEY}"})
    return response.json()

def get_technicians():
    response = requests.get(f"{API_URL}/technicians", headers={"Authorization": f"Bearer {API_KEY}"})
    return response.json()

def assign_ticket(ticket_id, technician_id):
    response = requests.post(
        f"{API_URL}/tickets/{ticket_id}/assign",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"technician_id": technician_id}
    )
    return response.status_code == 200
```

### `app.py`
```python
from flask import Flask, request, jsonify, render_template
from agidesk_api import get_unassigned_tickets, get_technicians, assign_ticket

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/tickets", methods=["GET"])
def tickets():
    return jsonify(get_unassigned_tickets())

@app.route("/technicians", methods=["GET"])
def technicians():
    return jsonify(get_technicians())

@app.route("/assign", methods=["POST"])
def assign():
    data = request.json
    if assign_ticket(data["ticket_id"], data["technician_id"]):
        return jsonify({"message": "Ticket assigned successfully."}), 200
    return jsonify({"error": "Failed to assign ticket."}), 400

if __name__ == "__main__":
    app.run(debug=True)
```

## 3. Frontend - Interface Web
### `index.html`
```html
<!DOCTYPE html>
<html>
<head>
    <title>Agidesk Ticket Manager</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <h1>Distribuição de Chamados</h1>
    <div class="container">
        <div id="tickets" class="column">
            <h2>Chamados</h2>
        </div>
        <div id="technicians" class="column">
            <h2>Técnicos</h2>
        </div>
    </div>
    <script src="app.js"></script>
</body>
</html>
```

### `styles.css`
```css
body {
    font-family: Arial, sans-serif;
}
.container {
    display: flex;
    gap: 20px;
}
.column {
    width: 45%;
    border: 2px solid #ccc;
    padding: 10px;
}
```

### `app.js`
```javascript
document.addEventListener("DOMContentLoaded", () => {
    const ticketsContainer = document.getElementById("tickets");
    const techniciansContainer = document.getElementById("technicians");

    async function loadTickets() {
        const response = await fetch("/tickets");
        const tickets = await response.json();
        tickets.forEach(ticket => {
            const div = document.createElement("div");
            div.textContent = `${ticket.id} - ${ticket.title}`;
            div.className = "ticket";
            div.draggable = true;
            div.dataset.ticketId = ticket.id;
            ticketsContainer.appendChild(div);
        });
    }

    async function loadTechnicians() {
        const response = await fetch("/technicians");
        const technicians = await response.json();
        technicians.forEach(tech => {
            const div = document.createElement("div");
            div.textContent = `${tech.name} (${tech.open_tickets} open)`;
            div.className = "technician";
            div.dataset.technicianId = tech.id;
            techniciansContainer.appendChild(div);
        });
    }

    loadTickets();
    loadTechnicians();
});
```

## 4. Execução do Projeto

### Backend
1. Configure o arquivo `.env` na pasta `backend`:
```env
API_KEY=sua_chave_api_agidesk
API_URL=url_da_api_agidesk
```

2. Execute o backend:
```bash
cd backend
python app.py
```
O servidor estará disponível em `http://seu_ip:5000`

### Frontend
1. Configure o arquivo `.env` na pasta `frontend`:
```env
VITE_API_URL=http://seu_ip:5000/api
```

2. Execute o frontend:
```bash
cd frontend
npm install
npm run dev
```
O frontend estará disponível em `http://localhost:5173`

### Acessando a Aplicação
- Localmente: Acesse `http://localhost:5173`
- Remotamente: Acesse `http://seu_ip:5173`

**Nota**: Certifique-se de que:
1. A porta 5000 está liberada no firewall para o backend
2. A porta 5173 está liberada no firewall para o frontend
3. O IP do servidor está acessível na rede

## 5. Melhores Práticas
- Utilize variáveis de ambiente para armazenar chaves de API.
- Implemente tratamento de erros robusto para lidar com falhas de conexão ou respostas inesperadas da API.
- Use padrões de projeto como MVC para manter o código organizado e escalável.

## 6. Possíveis Melhorias Futuras
- Adicionar um sistema de notificações para avisar os técnicos sobre novos chamados.
- Implementar filtros para facilitar a busca por chamados ou técnicos.
- Melhorar a interface gráfica com elementos visuais mais atrativos e intuitivos.

