---
sidebar_position: 4
title: Nexus Usage
---

Once the components artifacts have been push on Nexus you have several methods to use them.

- You can connect to the docker registry to retrieve the docker images that have been pushed on it. As the Nexus is connected to the Keycloak, the IRT SystemX credentials allows you to connect to the registry.

- You can also connect to the Nexus python repo with the IRT SystemX credentials.

Here are several methods to connect to the Nexus repo :

### Nexus with Jupyter

You need to create a configuration file so that you can install libs from the Nexus. You will then have access to the libraries developed by the different projects of the program. 

Create a file **pip.conf** here **/home/jovyan/.config/pip/pip.conf**, with the following contents :

```
[global]
index = https://repo.irtsysx.fr/repository/pypi-releases
index-url = https://repo.irtsysx.fr/repository/pypi-public/simple
no-cache-dir = false
```

Your IRT SystemX credentials will be required when you run _pip install_ command.

### Nexus with airflow

You need to add the nexus configuration on the Dockerfile of the Docker image that you want to run with airflow.

Dockerfile example :

```
FROM python:3.10.5-slim

ARG USER_NEXUS
ARG PASSWORD_NEXUS

WORKDIR /app

COPY main.py ./
COPY requirements.txt ./

RUN pip install -i https://$USER_NEXUS:$PASSWORD_NEXUS@repo.irtsysx.fr/repository/pypi-public/simple  -r requirements.txt


CMD [ "python", "./main.py"]
```

If you are building the docker image manually, you don't need __ARG USER_NEXUS__ and the __ARG PASSWORD_NEXUS__ line, and you can replace $USER_NEXUS:$PASSWORD_NEXUS with your IRT SystemX credentials.

But if you want to build your docker image with the pipeline gitlab-ci available, you need to use this template of Dockerfile and keep  __ARG USER_NEXUS__, __ARG PASSWORD_NEXUS__ and $USER_NEXUS:$PASSWORD_NEXUS. These variables will be fill by the pipeline with a Nexus service account that authozise to read the python repository.

