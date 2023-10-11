import sys
import socket
from datetime import datetime
import docker
dockerClient = docker.from_env()

# get list of containers
def getContainers():
    containersReturn = []
    containers = dockerClient.containers.list(all=True)
    for container in containers:
        containersReturn.append(container.id)
        print(container.id)
    return containersReturn

# get status of containers with container_id
def get_status_Containers(container_id:str):
    try:
        containers = dockerClient.containers.get(container_id)
    except:
        return None
    container_state = containers.attrs["State"]
    return container_state["Status"]

# create containers with loaded docker images
def create_docker_run(image_name:str, user:int):
    dockerClient.containers.run(image_name, "sleep infinity", detach=True)

# checkout enabled ports
def checkout_ports():
    # Defining a target
    ip = socket.gethostbyname (socket.gethostname())  #getting ip-address of host
 
    for port in range(65535):      #check for all available ports
    
        try:
    
            serv = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # create a new socket
    
            serv.bind((ip,port)) # bind socket with address
                
        except:
    
            print('[OPEN] Port open :',port) #print open port number

        serv.close() #close connection

# create container with image_name
def create_docker_run(image_name:str, user:int):
    dockerClient.containers.run(image_name, "sleep infinity", detach=True)

# restart the bot container with docker container id
def start_containers(container_id:str):
    try:
        containers = dockerClient.containers.get(container_id)
    except:
        return None
    containers.start()
    container_state = containers.attrs["State"]
    return container_state["Status"]

# stop the bot container with docker container id
def stop_containers(container_id:str):
    try:
        containers = dockerClient.containers.get(container_id)
    except:
        return None
    containers.stop()
    container_state = containers.attrs["State"]
    return container_state["Status"]

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

if __name__ == '__main__':
    print(getContainers())
    print(get_status_Containers("5a7249db0be943566135a5729"))

    # create_docker_run("bot:test", 1)
    # print(stop_containers("ae45490812fb5266149c4c8eac91751394e21263237373494a1022f3d1eab5fd"))

    # print(start_containers("ae45490812fb5266149c4c8eac91751394e21263237373494a1022f3d1eab5fd"))
    print(remove_containers("ae45490812fb5266149c4c8eac91751394e21263237373494a1022f3d1eab5fd"))

    checkout_ports()