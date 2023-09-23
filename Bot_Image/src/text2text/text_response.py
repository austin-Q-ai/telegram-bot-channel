from dotenv import load_dotenv
import json
import requests
import os
from src.handle_issues import handle_issues as issue

load_dotenv(dotenv_path='config.env')

BRAIN_SERVICE = os.getenv('BRAIN_SERVICE')
BRAIN_KEY = os.getenv('BRAIN_KEY')
BRAIN_ID = os.getenv('BRAIN_ID')

def get_response(chat_id:str, text:str):
    url= f'{BRAIN_SERVICE}/chat/{chat_id}/question'
    headers = {'Authorization': f'Bearer {BRAIN_KEY}',  "Content-Type": "application/json"}
    params = {'brain_id': BRAIN_ID}
    data = {'question': text}
    try:
        response = requests.post(
            url=url, 
            headers=headers,
            params=params,
            json=data
        )
    except:
        return issue.brain_server_error(url)
        
    if response.status_code == 200:
        return response.json()["assistant"]
    else:
        return issue.expert_brain_key_error(url, response)