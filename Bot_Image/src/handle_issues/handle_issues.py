from dotenv import load_dotenv
import json
import requests
import os
from .default_answer import ANSWER_1, ANSWER_2

load_dotenv(dotenv_path='config.env')

BOT_CONTROLLER = os.getenv('BOT_CONTROLLER')
Telegram_key = os.getenv('Telegram_key')

VIDEO_SERVICE = os.getenv("VIDEO_SERVICE")
VIDEO_KEY = os.getenv('VIDEO_KEY')

# Report errors in connection to APIs
def report_controller(url:str, status:int, description:str):
    print("Error: ", url, status, description)
    url = f'{BOT_CONTROLLER}/reporter'
    data = {
        "url": url,
        "status":status,
        "description":description
        }
    headers={'Authorization': f'Bearer {Telegram_key}'}
    try:
        response = requests.post(
            url=url,
            json=data,
            headers=headers
            )
    except:
        pass

# Failed to connect to service
def brain_server_error(url):
    report_controller(url, 0, "Failed to connect server")
    return ANSWER_1

def video_server_error(url):
    report_controller(url, 0, "Failed to connect server")
    return ANSWER_2

# Errors in Expert Brain Key
def expert_brain_key_error(url, res):
    if res.status_code == 401:
        report_controller(url, 401, res.json()["detail"])
    elif res.status_code == 500:
        report_controller(url, 500, "Internal Error")
    else:
        report_controller(url, res.status_code, res.content)
    return ANSWER_1

# Errors in Expert Brain Key
def video_key_error(url, res):
    if res.status_code == 401:
        report_controller(url, 401, res.json()["detail"])
    elif res.status_code == 500:
        report_controller(url, 500, "Internal Error")
    else:
        report_controller(url, res.status_code, res.content)
    return ANSWER_2

def generating_default_answer(file_path):
    url= f'{VIDEO_SERVICE}/tts/{VIDEO_KEY}/video/'
    data = {
        "text":ANSWER_1
    }
    try:
        response = requests.get(
            url=url,
            json = data
        )
    except:
        video_server_error(url)
        return False
    
    if response.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(response.content)
        return True
    else:
        expert_brain_key_error(url, response)
        return False


def checkout_default_answer():
    os.makedirs("default_answer", exist_ok=True)
    file_path = "default_answer/answer_1.mp4"
    if not os.path.exists(file_path):
        return generating_default_answer(file_path)
    return True