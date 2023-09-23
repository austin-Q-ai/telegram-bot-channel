import docker
dockerClient = docker.from_env()


def getContainers():
    containersReturn = []
    containers = dockerClient.containers.list(all=True)
    for container in containers:
        print(container.id)
    return containersReturn


def get_status_Containers():
    containers = dockerClient.containers.get("3bc8f03d72eb3b49ffe17963fbbb5146c16134e4d50d5c67c86ff61076fe28dc")
    status = containers.inspect()['Status']['State']
    return status

def removeContainers():
    containers = getContainers()
    for container in containers:
        if imageName in str(container.image):
            print("Deleting old container {}".format(container.name))
            try:
                container.stop()
                container.remove()
            except Exception as e:
                print("Error deleting old container {}".format(container.name))
                print(e)

def runContainer(testType,dataframeN):
    images = dockerClient.images.list(all=True)
    if imageName in ' '.join(map(str, images)):
        print("Image exist, starting container..")
        dockerClient.containers.run(imageName+":latest", environment = {"TEST_TYPE":testType,"DATAFRAME_N":dataframeN,"CALC_N":calcN})
    else:
        print("Image doesn't exist, need to create it!")
        dockerClient.images.build(path = "./", tag = imageName)
        dockerClient.containers.run(imageName+":latest", environment = {"TEST_TYPE":testType,"DATAFRAME_N":dataframeN,"CALC_N":calcN})

# restart the bot container with docker container id
def start_bot(bot_id:str):
    containers = getContainers()
    for container in containers:
        if imageName in str(container.image):
            print("Deleting old container {}".format(container.name))
            try:
                container.start()
            except Exception as e:
                print("Error deleting old container {}".format(container.name))
                print(e)

# stop the bot container with docker container id
def stop_bot(bot_id:str):
    containers = getContainers()
    for container in containers:
        if imageName in str(container.image):
            print("Deleting old container {}".format(container.name))
            try:
                container.stop()
            except Exception as e:
                print("Error deleting old container {}".format(container.name))
                print(e)

# delete the bot container with docker container id
def remove_bot(bot_id:str):
    containers = getContainers()
    for container in containers:
        if imageName in str(container.image):
            print("Deleting old container {}".format(container.name))
            try:
                container.stop()
                container.remove()
            except Exception as e:
                print("Error deleting old container {}".format(container.name))
                print(e)

if __name__ == '__main__':
    print(getContainers())
    print(get_status_Containers())