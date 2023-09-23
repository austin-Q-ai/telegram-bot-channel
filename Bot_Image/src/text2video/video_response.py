from dotenv import load_dotenv
import json
import requests
import os
from src.handle_issues import handle_issues as issue

load_dotenv(dotenv_path='config.env')

VIDEO_SERVICE = os.getenv("VIDEO_SERVICE")
VIDEO_KEY = os.getenv('VIDEO_KEY')
# def get_response(chat_id:str, text:str):

def get_video_response(text:str):
    url= f'{VIDEO_SERVICE}/tts/{VIDEO_KEY}/video/'
    data = {
        "text":text
    }
    try:
        response = requests.get(
            url=url,
            json = data
        )
    except:
        return issue.video_server_error(url)
    if response.status_code == 200:
        return response.content
    else:
        return issue.video_key_error(url, response)