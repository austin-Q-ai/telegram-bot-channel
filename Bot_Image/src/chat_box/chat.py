from dotenv import load_dotenv
import json
import os
import requests
from ..handle_issues import handle_issues as issues

load_dotenv(dotenv_path='config.env')

BRAIN_SERVICE = os.getenv('BRAIN_SERVICE')
BRAIN_KEY = os.getenv('BRAIN_KEY')

def greate_chat(id:int):
    url= f'{BRAIN_SERVICE}/chat'
    data = {
        "name": str(id)
        }
    headers={'Authorization': f'Bearer {BRAIN_KEY}'}
    try:
        response = requests.post(
            url=url,
            json=data,
            headers=headers
            )
    except:
        return False, issues.brain_server_error(url)

    if response.status_code == 200:
        return True, response.json()["chat_id"]
    else:
        return False, issues.expert_brain_key_error(url, response)