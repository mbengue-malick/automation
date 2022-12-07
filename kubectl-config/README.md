# Kubectl config

## Disclaimer

Cette configuration automatisée ne fonctionne que sur :

- Linux
- Microsoft WSL 2

Pour installer et configurer kubectl et les outils de login IRT sur Windows, des modifications seront à faire sur le script python, et l'installation devra être faite manuellement.

## Installation

Lancer le script `install_and_config_kubectl.sh`.

~~~bash
mpatron@ITEM-S76640:~$ ./install_and_config_kubectl.sh
~~~

## Connexion à un cluster

- Pour se connecter au cluster Confiance.AI interne : `k login confianceai-interne`

- Pour se connecter au cluster Confiance.AI public (OVH) : `k login confianceai-public`

- Pour se connecter au cluster Confiance.AI public-v2 (OVH) : `k login public-v2`

> Les identifiants sont vos identifiants keycloak.

### Config backup

Dans le cas où une config kubectl exite déjà, le script en fait un backup avant toute manipulation.

Le script est capable de compléter une configuration existante, ou d'en recréer une nouvelle.

### Exemple de dérouler utilisateur

~~~bash
mpatron@ITEM-S76640:~$ git clone git@git.irt-systemx.fr:confianceai/ec_1/fa2_infrastructure/kubectl-config.git
Cloning into 'kubectl-config'...
remote: Enumerating objects: 19, done.
remote: Counting objects: 100% (19/19), done.
remote: Compressing objects: 100% (17/17), done.
remote: Total 19 (delta 6), reused 0 (delta 0), pack-reused 0
Receiving objects: 100% (19/19), 11.18 KiB | 5.59 MiB/s, done.
Resolving deltas: 100% (6/6), done.

mpatron@ITEM-S76640:~$ cd kubectl-config/

mpatron@ITEM-S76640:~$ ls
README.md  README.md.bak  config  config.yaml  install_and_config_kubectl.sh  kubectl-ctx.sh  kubectl-login.py

mpatron@ITEM-S76640:~$ ./install_and_config_kubectl.sh
What's your LDAP username (firstname.lastname):
mickael.patron
What's your target namespace (usually your main project name, e.g.: SVA):
tst
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 41.9M  100 41.9M    0     0  3226k      0  0:00:13  0:00:13 --:--:-- 4704k
[sudo] password for mpatron:

# Installation and configuration done !

You can now use kubectl to manage your namespace.
1. Authenticate with `kubectl login` and use `kubectl` (or the shorthand `k`) to query the cluster
2. Try :
  kubectl run nginx-test --image nginxdemos/hello --port 80 --expose
  kubectl get all
  kubectl logs -f $(kubectl get pods | awk 'NR==2 {print $1}')

mpatron@ITEM-S76640:~$ kubectl login public-v2
Loging in to cluster: public-v2
Input your username (mickael.patron):
Password for mickael.patron:
User "public-v2-mickael.patron" set.
Context "public-v2" modified.
Switched to context "public-v2".

mpatron@ITEM-S76640:~$ kubectl get nodes
NAME                            STATUS   ROLES                  AGE   VERSION
master0-confianceai-public-v2   Ready    control-plane,master   24d   v1.23.6
master1-confianceai-public-v2   Ready    control-plane,master   23d   v1.23.6
master2-confianceai-public-v2   Ready    control-plane,master   23d   v1.23.6
worker0-confianceai-public-v2   Ready    worker                 23d   v1.23.6
worker1-confianceai-public-v2   Ready    worker                 23d   v1.23.6
worker2-confianceai-public-v2   Ready    worker                 23d   v1.23.6
worker3-confianceai-public-v2   Ready    worker                 23d   v1.23.6
~~~
