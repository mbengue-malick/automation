---
sidebar_position: 3
title: Nodes
---

## Preparation

The following parts have to be applied on every node, master **and** worker.

### Firewall

First allow the following ports the VMs' firewall so that flows can reach your Kubernetes cluster:

- For master nodes: `22/tcp`, `179/tcp`, `6443/tcp`, `2379-2380/tcp`, `6641-6642/tcp`, `53/tcp`, `9000-9999/tcp`, `9000-9999/udp`, `6081/udp`, `4789/udp`, `4500/udp`, `500/udp`, `30000-32767/udp`, `22623/tcp`, `10250/tcp`, `10251/tcp`, `10252/tcp`, `10255/tcp`, `10257/tcp`, `10259/tcp`, `3300/tcp`, `6789/tcp`, `6800-7300/tcp`
- For worker nodes: `22/tcp`, `179/tcp`, `80/tcp`, `3300/tcp`, `6789/tcp`, `6800-7300/tcp`, `443/tcp`, `30000-32767/tcp`, `10250/tcp`, `10255/tcp`, `9000-9999/tcp`, `9000-9999/udp`, `6081/udp`, `4789/udp`, `4500/udp`, `500/udp`, `30000-32767/udp`, `1936/tcp`

Once the VMs are ready, connect to them with SSH and perform the actions below.

### Update the instances and install the necessary components for Kubernetes

Update Kubernetes servers:

```bash
sudo apt update
sudo apt -y full-upgrade
[ -f /var/run/reboot-required ] && sudo reboot -f
```

Install kubelet, kubeadm and kubectl:

```bash
sudo apt -y install curl apt-transport-https
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt update
sudo apt -y install vim git curl wget kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl
```

Check that the installation has been completed with the following command: `kubectl version --client && kubeadm version`.

Disable Swap:

```bash
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab
sudo swapoff -a
```

For instance preparation, since Kubernetes deprecates Docker, we will use Containerd as the runtime:

- Configure persistent Loading of modules

```bash
sudo tee /etc/modules-load.d/containerd.conf <<EOF \
overlay \
br_netfilter \
EOF
```

- Load at runtime

```bash
sudo modprobe overlay
sudo modprobe br_netfilter
```

- Ensure sysctl params are set

```bash
sudo tee /etc/sysctl.d/kubernetes.conf<<EOF \
net.bridge.bridge-nf-call-ip6tables = 1 \
net.bridge.bridge-nf-call-iptables = 1 \
net.ipv4.ip_forward = 1 \
EOF
```

- Reload configs

```bash
sudo sysctl --system
```

- Install required packages

```bash
sudo apt install -y curl gnupg2 software-properties-common apt-transport-https ca-certificates
```

- Add Docker repo

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
```

- Install containerd

```bash
sudo apt update
sudo apt install -y containerd.io=1.5.11-1
sudo apt-mark hold containerd.io
```

- Configure containerd and start service

```bash
sudo su -
mkdir -p /etc/containerd
containerd config default>/etc/containerd/config.toml
```

- Restart containerd

```bash
sudo systemctl restart containerd
sudo systemctl enable containerd
systemctl status  containerd
```

## Initializing the master nodes

Now connect to the first master node. Once the connection is established, we will execute the commands below.

First enable kubelet service:

```bash
sudo systemctl enable kubelet
sudo kubeadm config images pull --cri-socket /run/containerd/containerd.sock
```

After that, pull container images:

```bash
sudo kubeadm config images pull --cri-socket /run/containerd/containerd.sock
```

Then, create the kubernetes cluster:

```bash
sudo kubeadm init --pod-network-cidr=192.168.0.0/16 --cri-socket /run/containerd/containerd.sock --upload-certs --control-plane-endpoint=api.<cluster-name>.<domain-name>:6443
```

This last command will give you 2 commands as output that you will perform later. The first one is for adding the other master nodes (control planes) and the last one is for adding the worker nodes (compute). Now, configure the config file to run the kubectl commands:

```bash
mkdir -p $HOME/.kube
sudo cp -f /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

Now you can add the other master nodes with the `kubectl join` command that was provided (the first one)


