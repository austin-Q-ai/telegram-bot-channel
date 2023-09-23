from deepgram import Deepgram
from argparse import ArgumentParser
import json
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='config.env')

DG_KEY = os.getenv('DG_KEY')

dg = Deepgram(DG_KEY)

params = {
    "punctuate": True,
    "model": 'general',
    "tier": 'nova',
    # 'api_key': dg_key
    }

def speech_to_text(id):
    # Save the file to disk
    speech_file = f'voice_message/{id}.ogg'
    with open(speech_file, "rb") as f:
        source = {"buffer": f, "mimetype": 'audio/' + "ogg"}
        res = dg.transcription.sync_prerecorded(source, params)
        with open("1.json", "w") as transcript:
            json.dump(res, transcript)
    data = json.load(open('1.json'))
    return data["results"]["channels"][0]["alternatives"][0]["transcript"]