---
sidebar_position: 4
title: Weave
---

Weave provides a network to connect all pods together.

Before installing weave you should make sure that the following ports are not blocked by the firewall: `6783/tcp`, `6783/udp` and `6784/udp`.

Weave can then be installed by running the following command on the master node:

```bash
kubectl apply -f "https://cloud.weave.works/k8s/net?k8s-version=$(kubectl version | base64 | tr -d '\n')"
```

After a few seconds, you should notice that all pods should be in the running state as well as all workers attached to the cluster.
