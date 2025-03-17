import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
from agidesk_api import get_unassigned_tickets, get_technicians, assign_ticket, id_tecnicos

load_dotenv()

# 18848 Fernando Brito
# 7304 Wilner
# 876 Cicero
# 5207 Fonte
# 18823 Julio
# 13132 Thailson
# 16740 Gelson
# 1241 Douglas
# 7957 Hyann
# 3637 Luis Fernando

id_tecnicos = ["18848", "7304", "876", "5207", "18823", "13132", "16740", "1241", "7957", "3637"]

API_KEY = os.getenv('API_KEY')
API_URL = os.getenv('API_URL')

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tickets')
def tickets():
    """Retorna os chamados não atribuídos"""
    chamados = get_unassigned_tickets()
    return jsonify([{
        'id': chamado.get('id'),
        'titulo': chamado.get('title'),
        'descricao': chamado.get('description'),
        'cliente': chamado.get('requester', {}).get('name', 'Cliente não identificado')
    } for chamado in chamados])

@app.route('/api/technicians')
def technicians():
    """Retorna a lista de técnicos"""
    tecnicos = get_technicians(id_tecnicos)
    return jsonify([{
        'id': tecnico['id'],
        'nome': tecnico['name'],
        'foto': tecnico['avatar_url'],
        'chamadosAtivos': tecnico['ticket_count']
    } for tecnico in tecnicos])

@app.route('/api/assign', methods=['POST'])
def assign():
    """Atribui um chamado a um técnico"""
    data = request.json
    success = assign_ticket(data['ticketId'], data['technicianId'])
    if success:
        return jsonify({'message': 'Chamado atribuído com sucesso'}), 200
    return jsonify({'error': 'Falha ao atribuir chamado'}), 400

if __name__ == '__main__':
    app.run(debug=True)