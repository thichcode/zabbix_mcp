import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

ZABBIX_API_URL = os.getenv("ZABBIX_API_URL")
ZABBIX_USER = os.getenv("ZABBIX_USER")
ZABBIX_PASSWORD = os.getenv("ZABBIX_PASSWORD")
MCP_WEBHOOK_URL = "http://localhost:8000/api/v1/webhook/zabbix"

def get_auth_token():
    payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": ZABBIX_USER,
            "password": ZABBIX_PASSWORD
        },
        "id": 1
    }
    
    response = requests.post(ZABBIX_API_URL, json=payload)
    return response.json()["result"]

def create_webhook_media_type(auth_token):
    payload = {
        "jsonrpc": "2.0",
        "method": "mediatype.create",
        "params": {
            "name": "MCP Webhook",
            "type": 4,  # Webhook
            "exec_path": f"curl -X POST -H 'Content-Type: application/json' -d '{{'event': ${{EVENT.DETAILS}}, 'action': ${{EVENT.ACTION}}}}' {MCP_WEBHOOK_URL}",
            "status": 0  # Enabled
        },
        "auth": auth_token,
        "id": 1
    }
    
    response = requests.post(ZABBIX_API_URL, json=payload)
    return response.json()["result"]["mediatypeids"][0]

def create_webhook_action(auth_token, media_type_id):
    payload = {
        "jsonrpc": "2.0",
        "method": "action.create",
        "params": {
            "name": "MCP Analysis",
            "eventsource": 0,  # Trigger
            "status": 0,  # Enabled
            "esc_period": 0,
            "def_shortdata": "MCP Analysis: {TRIGGER.NAME}",
            "def_longdata": "MCP Analysis for {TRIGGER.NAME} on {HOST.NAME}",
            "operations": [
                {
                    "operationtype": 0,  # Send message
                    "opmessage_usr": [
                        {
                            "userid": "1"  # Admin user
                        }
                    ],
                    "opmessage": {
                        "default_msg": 1,
                        "mediatypeid": media_type_id
                    }
                }
            ],
            "recovery_operations": [],
            "ack_operations": []
        },
        "auth": auth_token,
        "id": 1
    }
    
    response = requests.post(ZABBIX_API_URL, json=payload)
    return response.json()["result"]["actionids"][0]

def main():
    try:
        # Get authentication token
        auth_token = get_auth_token()
        print("Authentication successful")
        
        # Create media type for webhook
        media_type_id = create_webhook_media_type(auth_token)
        print(f"Created webhook media type with ID: {media_type_id}")
        
        # Create action for webhook
        action_id = create_webhook_action(auth_token, media_type_id)
        print(f"Created webhook action with ID: {action_id}")
        
        print("Zabbix configuration completed successfully")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 