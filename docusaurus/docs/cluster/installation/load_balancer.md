---
sidebar_position: 2
title: Load Balancer
---

You need to configure 2 LoadBalancers in front of the Kubernetes cluster:

- One dedicated to the Kubernetes API (port `6443/tcp`), it will redirect its flow to ports 6443 of the master nodes. You will have to declare a domain name on the IP of the LoadBalancer, it should have the following form: `api.<cluster-name>.<domain-name>`.

- One dedicated to the INGRESS of Kubernetes (port `80/tcp` & `443/tcp`), it will redirect its flow to the ports of the Traefik pods which will be on the worker nodes. You will have to declare a domain name on the IP of the LoadBalancer, this one will have the following form: `*.apps.<cluster-name>.<domain-name>`.
