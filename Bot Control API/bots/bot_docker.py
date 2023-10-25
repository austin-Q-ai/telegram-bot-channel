import socket
import docker
import sqlite3
import requests

from dotenv import load_dotenv
import os, sys

load_dotenv(dotenv_path='config.env')

DG_KEY = os.getenv("DG_KEY")
BRAIN_SERVICE = os.getenv('BRAIN_SERVICE')
VIDEO_SERVICE = os.getenv('VIDEO_SERVICE')
BOT_CONTROLLER = os.getenv('BOT_CONTROLLER')

dockerClient = docker.from_env()

def load_docker_image():
    path = "/home/bot-factory/Bot Control API/bot_image.tar"
    with open("/home/bot-factory/Bot Control API/bot_image.tar", "rb") as f:
        image = dockerClient.images.load(f)
    return image[0].tags[0]

def save_docker(container_id:str):
    image = dockerClient.images.get("busybox:latest")
    f = open('/tmp/busybox-latest.tar', 'wb')
    for chunk in image.save():
        f.write(chunk)
    f.close()


# get status of containers with container_id
def get_status_Containers(container_id:str):
    try:
        containers = dockerClient.containers.get(container_id)
    except:
        return None
    container_state = containers.attrs["State"]
    return container_state["Status"]

# checkout enabled ports
def checkout_ports():
    # Defining a target
    ip = socket.gethostbyname (socket.gethostname())  #getting ip-address of host
    enable_port:int
    for port in range(500, 65535):      #check for all available ports
        try:
            serv = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # create a new socket
            serv.bind((ip, port)) # bind socket with address
            enable_port = port
            serv.close()
            break
        except:
            print('[OPEN] Port open :', port) #print open port number
            serv.close() #close connection
    return enable_port

# create container with image_name
def create_docker_run(image_name:str, container_name:str, config_file_path:str, db_file_path:str):
    port = checkout_ports()
    volume = {}
    volume[config_file_path] = {'bind': '/telegram-bot/config.env', 'mode': 'ro'}
    volume[db_file_path] = {'bind': '/telegram-bot/bot_user.db', 'mode': 'rw'}
    k = dockerClient.containers.run(
        image=image_name, 
        name=container_name, 
        detach=True, 
        ports={'8080':port},
        volumes=volume
    )
    return k.id

# restart the bot container with docker container id
def start_containers(container_id:str):
    try:
        containers = dockerClient.containers.get(container_id)
        containers.start()
        return True
    except:
        return False

# stop the bot container with docker container id
def stop_containers(container_id:str):
    try:
        containers = dockerClient.containers.get(container_id)
        containers.stop()
        return True
    except:
        return False

# delete the bot container with docker container id
def remove_containers(container_id:str):
    try:
        containers = dockerClient.containers.get(container_id)
    except:
        return None
    containers.stop()
    containers.remove()
    container_state = containers.attrs["State"]
    return container_state["Status"]

# create bot config env
def create_config_env(brain_api:str, brain_id:str, video_api:str, video_id:str, bot_token:str, bot_name:str, bot_username:str):
    lines = []
    lines.append(f'DG_KEY = {DG_KEY}\n')
    lines.append(f'BRAIN_SERVICE = {BRAIN_SERVICE}\n')
    lines.append(f'BRAIN_KEY = {brain_api}\n')
    lines.append(f'BRAIN_ID = {brain_id}\n')

    lines.append(f'VIDEO_SERVICE = {VIDEO_SERVICE}\n')
    lines.append(f'VIDEO_KEY = {video_api}\n')
    lines.append(f'VIDEO_ID = {video_id}\n')
    lines.append(f'Telegram_key= {bot_token}\n')
    lines.append(f'Bot_name = {bot_name}\n')
    
    os.makedirs("config", exist_ok=True)
    config_file_name = f'config/{bot_username}.env'
    dir_path = os.path.abspath(config_file_name)
    print(dir_path)
    try:
        with open(config_file_name, "w") as config:
            config.writelines(lines)
        return dir_path
    except:
        return False

def delete_chat_room(BRAIN_KEY:str, chat_id:str):
    url= f'{BRAIN_SERVICE}/chat/{chat_id}'
    data = {
        "name": str(id)
        }
    headers={'Authorization': f'Bearer {BRAIN_KEY}'}
    try:
        response = requests.delete(
            url=url,
            headers=headers
            )
    except:
        return False

    if response.status_code == 200:
        return True
    else:
        return False

def create_bot_db(bot_username:str):
    db_file_name = f'config/{bot_username}.db'
    dir_path = os.path.abspath(db_file_name)
    print(dir_path)
    mydb = sqlite3.connect(db_file_name)
    mydb.execute("CREATE TABLE IF NOT EXISTS users (id BIGINT PRIMARY KEY, chat_id VARCHAR(255) UNIQUE NOT NULL, response TEXT NULL);")
    mydb.close()
    return dir_path

def delete_bot_chat_room(bot_username:str, BRAIN_KEY:str):
    db_path = f'config/{bot_username}.db'
    config_path = f'config/{bot_username}.env'
    mydb = sqlite3.connect(db_path)
    chat_rooms = list(mydb.execute("Select * from users"))
    for chat_room in chat_rooms:
        chat_id = chat_room[1]
        delete_chat_room(BRAIN_KEY, chat_id)
    mydb.close()
    os.remove(db_path)
    os.remove(config_path)

if __name__ == '__main__':
    # print(getContainers())
    # print(get_status_Containers("5a7249db0be943566135a5729")) 
    #  
    # # create_docker_run("bot:test", 1)
    # # print(stop_containers("ae45490812fb5266149c4c8eac91751394e21263237373494a1022f3d1eab5fd"))

    # # print(start_containers("ae45490812fb5266149c4c8eac91751394e21263237373494a1022f3d1eab5fd"))
    # print(remove_containers("ae45490812fb5266149c4c8eac91751394e21263237373494a1022f3d1eab5fd"))

    # create_config_env(
    #     brain_api="8c0a302245c45485b9433c1020be06bf",
    #     brain_id="6c23b41d-94e1-4883-9a27-63532ece8691",
    #     video_api="zLyL5oBpnNzFE3Ebzhk0ZUTv1AG0t8lCXq3JxRcMyTYFtOxpwh",
    #     bot_token="5992691054:AAFIfElI9ilnUTqA2ev4iRP2ffKyam05ols",
    #     bot_name="Christophe KOURDOULY",
    #     bot_username="@christophe_mygpt_bot"
    # )
    print(load_docker_image())