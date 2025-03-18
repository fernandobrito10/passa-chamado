import requests
import urllib3
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')

id_tecnicos = ["7304", "876", "5207", "16740", "1241", "7957", "18848", "18823", "3637", "13132"]

# Desabilitar avisos de SSL inseguro
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_unassigned_tickets():
    """
    Obtém todos os chamados não atribuídos do Agidesk (sem responsável)
    """
    api_url = "https://grendene.agidesk.com/api/v1/issues"
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Tenant-ID": "grendene",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    params = {
        "app_key": API_KEY,
        "team": "14",
        "forecast": "teams",
        "active": "1"
    }
    
    try:
        response = requests.get(
            api_url,
            params=params,
            headers=headers,
            verify=False  # Desabilita verificação SSL
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Filtra apenas os chamados sem responsável
        tickets_without_responsible = [
            task for task in data
            if not task.get('responsible_id')
        ]
        print(f"Chamados em aberto: {tickets_without_responsible}")
        return tickets_without_responsible
        
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter chamados: {e}")
        return []

def get_technicians(id_tecnicos):
    """
    Obtém informações de técnicos e conta quantos chamados cada um tem
    
    Args:
        id_tecnicos: Lista com os IDs dos técnicos a serem buscados
    
    Returns:
        Lista de técnicos com seus nomes, fotos de perfil e contagem de chamados
    """
    technicians = []
    
    # Cabeçalhos para as requisições
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Tenant-ID": "grendene",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    try:
        # Primeiro, buscar todos os chamados para contar por técnico
        params_tickets = {
            "app_key": API_KEY,
            "team": "14",
            "forecast": "teams",
            "active": "1"
        }
        
        response_tickets = requests.get(
            "https://grendene.agidesk.com/api/v1/issues",
            params=params_tickets,
            headers=headers,
            verify=False
        )
        response_tickets.raise_for_status()
        
        tickets_data = response_tickets.json()
        
        # Inicializar contador de chamados por técnico
        ticket_counts = {int(tech_id): 0 for tech_id in id_tecnicos}
        
        # Contar chamados por técnico
        if isinstance(tickets_data, list):
            for ticket in tickets_data:
                responsible_id = ticket.get('responsible_id')
                if responsible_id:
                    # Converter para inteiro para comparação
                    try:
                        resp_id = int(responsible_id)
                        # Verificar se o ID está na nossa lista de técnicos
                        if resp_id in ticket_counts:
                            ticket_counts[resp_id] += 1
                    except (ValueError, TypeError):
                        # Ignorar IDs que não podem ser convertidos para inteiro
                        continue
        
        # Agora, buscar informações de cada técnico
        for tech_id in id_tecnicos:
            try:
                tech_id_int = int(tech_id)  # Garantir que tech_id seja inteiro
                
                params = {
                    "app_key": API_KEY,
                    "id": tech_id
                }
                
                response = requests.get(
                    "https://grendene.agidesk.com/api/v1/contacts",
                    params=params,
                    headers=headers,
                    verify=False
                )
                response.raise_for_status()
                
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    tech = data[0]
                    
                    tech_info = {
                        "id": tech.get("id"),
                        "name": tech.get("title", "Sem nome"),
                        "ticket_count": ticket_counts.get(tech_id_int, 0)  # Usar get() para evitar KeyError
                    }
                    
                    # Extrair a URL do avatar
                    avatar = tech.get("avatar")
                    if avatar and isinstance(avatar, dict):
                        tech_info["avatar_url"] = avatar.get("path", "")
                    else:
                        tech_info["avatar_url"] = ""
                    
                    technicians.append(tech_info)
                    print(f"Técnico: {tech_info['name']} (ID: {tech_info['id']}) - {tech_info['ticket_count']} chamados")
                
            except requests.exceptions.RequestException as e:
                print(f"Erro ao obter técnico com ID {tech_id}: {e}")
                continue
            except Exception as e:
                print(f"Erro ao processar técnico com ID {tech_id}: {e}")
                continue
        
        return technicians
        
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter contagem de chamados: {e}")
        return []    
def assign_ticket(ticket_id, technician_id):
    """
    Atribui um chamado a um técnico específico usando a API de transferência
    
    Args:
        ticket_id: ID do atendimento/chamado
        technician_id: ID do técnico que receberá o atendimento
        
    Returns:
        bool: True se a atribuição foi bem-sucedida, False caso contrário
    """
    # URL para a API de transferência
    transfer_url = f"https://grendene.agidesk.com/api/v1/tasks/{ticket_id}/transfer"
    
    # Parâmetros da query string
    params = {
        "app_key": API_KEY
    }
    
    # Cabeçalhos da requisição
    headers = {
        "Content-Type": "application/json",
        "X-Tenant-ID": "grendene",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # Corpo da requisição
    data = {
        "responsible_id": technician_id,
        "team_id": 14
    }
    
    try:
        response = requests.put(
            transfer_url,
            params=params,
            headers=headers,
            json=data,  # Usando json= para enviar o corpo como JSON
            verify=False  # Desabilita verificação SSL
        )
        
        response.raise_for_status()
        print(f"Chamado {ticket_id} atribuído com sucesso ao técnico {technician_id}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Erro ao atribuir chamado {ticket_id} ao técnico {technician_id}: {e}")
        return False

get_unassigned_tickets()
get_technicians(id_tecnicos)