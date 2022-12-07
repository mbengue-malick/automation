#!/usr/bin/env bash
#title          : install_and_config_kubectl.sh
#description    : This script installs and configures kubectl for IRT clusters
#author         : Pierre d'Aviau de Ternay<pierre.daviaudeternay@irt-systemx.fr>
#=============================================================================

## Retrieve user ldap id
echo "What's your LDAP username (firstname.lastname): "
read username
echo "What's your target namespace (usually your main project name, e.g.: SVA): "
read project

## Download and install kubectl
curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.18.5/bin/linux/amd64/kubectl
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl
# Trying to create the `k` shorthand for `kubectl`
sudo ln -s /usr/local/bin/kubectl /usr/local/bin/k &>/dev/null

## Replace kubectl config
mkdir -p ~/.kube
mv ~/.kube/config ~/.kube/config.kubectl-config.bak &>/dev/null
cp ./config ~/.kube/config
sed -i "s/{{username}}/$username/g" ~/.kube/config

## Set kubectl-login wrapper config
mkdir -p ~/.kube/kube-login
# Trying existing kubectl-login config backup
mv ~/.kube/kube-login/config.yaml ~/.kube/kube-login/config.yaml.kubectl-config.bak &>/dev/null
cp ./config.yaml ~/.kube/kube-login/config.yaml
sed -i "s/{{username}}/$username/g" ~/.kube/kube-login/config.yaml

## Setup kubectl-login
sudo chmod +x kubectl-login.py
sudo cp kubectl-login.py ~/.kube/kube-login/kubectl-login.py
# Trying to create the `kubectl-login` shorthand for `kubectl-login.py`
sudo ln -s ~/.kube/kube-login/kubectl-login.py /usr/local/bin/kubectl-login &>/dev/null

## Setup kubectl-ctx
sudo chmod +x kubectl-ctx.sh
sudo cp kubectl-ctx.sh ~/.kube/kube-login/kubectl-ctx.sh
# Trying to create the `kubectl-ctx` shorthand for `kubectl-ctx.sh`
sudo ln -s ~/.kube/kube-login/kubectl-ctx.sh /usr/local/bin/kubectl-ctx &>/dev/null

## Done
cat << 'EOF'

# Installation and configuration done !

You can now use kubectl to manage your namespace.
1. Authenticate with `kubectl login` and use `kubectl` (or the shorthand `k`) to query the cluster
2. Try :
  kubectl run nginx-test --image nginxdemos/hello --port 80 --expose
  kubectl get all
  kubectl logs -f $(kubectl get pods | awk 'NR==2 {print $1}')
EOF
