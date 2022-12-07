#!/usr/bin/python3
__title__       = "kubectl.py"
__description__ = "Wraps OIDC token distribution for kubectl, asking for the user's credentials"
__author__      = ["Pierre d'Aviau de Ternay<pierre.daviaudeternay@irt-systemx.fr>", "Jean-Alexis Lauricella<jean-alexis.lauricella@irt-systemx.fr>"]
__maintainer__  = ["Pierre d'Aviau de Ternay<pierre.daviaudeternay@irt-systemx.fr>", "Jean-Alexis Lauricella<jean-alexis.lauricella@irt-systemx.fr>"]

import requests
import getpass
import os
import urllib.parse
from subprocess import call
import sys
import yaml

osdir = os.environ["HOME"] + '/.kube/kube-login'

def initConf():
    '''
    kube-login config initialisation
    
    Looks for a kube-login config and creates it if it doesn't already exist
    '''
    if not os.path.exists(osdir):
        os.makedirs(osdir)
    if not os.path.isfile(osdir + '/config.yaml'):
        os.mknod(osdir + '/config.yaml')
        config = {
            'current_cluster': 'interne', 
            'username': '', 
            'clusters': {
                'interne': {
                    'client_secret' : 'bedc7a29-ee3c-45c4-842e-8ccacf796ec0',
                    'realm_url': 'https://keycloak.irtsysx.fr/auth/realms/smite',
                    'token_url': 'https://keycloak.irtsysx.fr/auth/realms/smite/protocol/openid-connect/token'
                }
            }
        }
        saveConf(osdir + '/config.yaml', config)

def loadConf(filepath):
    '''
    kube-login config loader
    
    Handles loading of a yaml file
    Args:
        filepath (str): The filepath of the yaml to load
    
    Returns:
        config: The yaml file loaded with safe_load()
    '''
    with open(filepath, 'r') as file:
        config = yaml.safe_load(file)
    return config

def saveConf(filepath, config):
    '''
    kube-login config saver
    
    Handles saving of a yaml file
    Args:
        filepath (str): The filepath of the yaml to save
        config (dict):  The dictionnary representing the yaml config
    '''
    with open(filepath, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)


if __name__ == '__main__':

    # Init conf if not existing, then load it
    initConf()
    config = loadConf(osdir + '/config.yaml')

    # Read Kubernetes variables from conf
    clusterName = config.get('current_cluster')
    userName = config.get('username')
    if userName == '' : userName = "name.surname"

    # Read cluster name from sys.argv if given
    tmp_clusterName = None
    if len(sys.argv) > 1:
        tmp_clusterName = sys.argv[1]
        print("Loging in to cluster: " + tmp_clusterName)

    # Read user input for cluster selection if not given in args and stash it in conf
    if not tmp_clusterName: tmp_clusterName = input('Input the name of the cluster to log in to (' + clusterName + '): ')
    clusterName = clusterName if (tmp_clusterName == "") else tmp_clusterName
    config['current_cluster'] = clusterName

    # Read user input for username selection and stash it in conf
    tmp_userName = input('Input your username (' + userName + '): ')
    userName = userName if tmp_userName == "" else tmp_userName
    config['username'] = userName

    # Read user input for password 
    userPassword = getpass.getpass('Password for ' + userName + ':')

    # Save conf for further utilization
    saveConf(osdir + '/config.yaml', config)

    # Prepare Keycloak request and kubectl config info
    payload = {}
    selectedCluster = config['clusters'][config['current_cluster']]
    keycloakClientSecret = selectedCluster["client_secret"]
    tokenUrl = selectedCluster["token_url"]
    realmUrl = selectedCluster["realm_url"]
    
    payload['scope'] = 'openid'
    payload['grant_type'] = 'password'
    payload['client_id'] = 'kubernetes'
    payload['client_secret'] = keycloakClientSecret
    payload['username'] = userName
    payload['password'] = userPassword

    r = requests.post(
        tokenUrl, 
        data=urllib.parse.urlencode(payload),
        headers={'Content-type': 'application/x-www-form-urlencoded'}
    )
    
    # Try Keycloak request to get OIDC tokens
    try:
        response = r.json()
    except BaseException as notJsonErr:
        print("Internal server error (500)")
        sys.exit(1)
    if 'error' in response:
        print(response['error_description'])
        sys.exit(1)

    # Get OIDC tokens and set OIDC conf in kubectl config
    refreshTokenKubectlArg = response['refresh_token']
    idTokenKubectlArg = response['id_token']
    call([
        'kubectl', 'config', 'set-credentials', config['current_cluster']+"-"+userName,
        '--auth-provider=oidc',
        '--auth-provider-arg=idp-issuer-url=' + realmUrl,
        '--auth-provider-arg=client-id=kubernetes',
        '--auth-provider-arg=client-secret=' + keycloakClientSecret,
        '--auth-provider-arg=refresh-token=' + refreshTokenKubectlArg,
        '--auth-provider-arg=id-token=' + idTokenKubectlArg
    ])

    # Configure context with the logged-in user (in case it's changed)
    call([
        'kubectl', 'config', 'set-context', config['current_cluster'], 
        '--cluster=' + config['current_cluster'], 
        '--user=' + config['current_cluster']+"-"+userName
    ])

    # Set the freshly configured context as the current context
    call(['kubectl', 'config', 'use-context', config['current_cluster']])