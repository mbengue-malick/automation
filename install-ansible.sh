#!/bin/bash

sudo apt remove ansible -y

sudo apt --purge autoremove -y

sudo apt update -y && sudo apt upgrade -y

sudo apt -y install software-properties-common

sudo apt-add-repository ppa:ansible/ansible -y

sudo apt update -y 

sudo apt install ansible -y

sudo apt install python3-argcomplete -y

sudo activate-global-python-argcomplete3

ansible --version
