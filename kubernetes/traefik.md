---
sidebar_position: 7
title: Traefik
---

## Installation

The installation is based on [this documentation](https://doc.traefik.io/traefik/getting-started/install-traefik/).

First, add the official helm repository and create a dedicated namespace on the cluster for Traefik:

```bash
helm repo add traefik https://helm.traefik.io/
helm repo update
kubectl create ns traefik
```

Then, get a local copy of the values file to configure it with your needs: `helm show values traefik/traefik > values.yaml`.

Be careful while configuring the values, as following the official documentation:

![Traefik configuration means exclusivity principle, from official documentation](/img/cluster/traefik_exclusivity.png)

Modify the values, and take especially care to the following lines:

```yaml
# values.yaml

initContainers:
  # The "volume-permissions" init container is required if you run into permission issues.
  # Related issue: https://github.com/traefik/traefik/issues/6972
  - name: volume-permissions
    image: busybox:1.31.1
    command: ["sh", "-c", "chmod -Rv 600 /data/*"]
    volumeMounts:
      - name: data
        mountPath: /data

# Be careful with the exclusivity principle (cf screen capture).
# The key additionalArguments must be unique in the file.
additionalArguments:
  # ACME configuration storage file to keep it persistent
  - "--certificatesresolvers.default.acme.storage=/data/acme.json"
  # OVH challenge configuration
  - "--certificatesresolvers.default.acme.dnschallenge.provider=ovh"
  - "--certificatesresolvers.default.acme.dnschallenge.delaybeforecheck=300"
  - "--certificatesresolvers.default.acme.httpchallenge.entrypoint=web"

# Read OVH credentials to use it as a DNS challenge provider, see paragraph below
envFrom:
  - secretRef:
      name: ovh-application-credentials

# Enable http to https redirection and TLS
ports:
  web:
    redirectTo: websecure
  tls:
    enabled: true
    certResolver: "default"

# Set the container security context
# To run the container with ports below 1024 this will need to be adjust to run as root
# This has to be modified if permission issues are faced during the deployment
securityContext:
  capabilities:
    drop: [ALL]
    add: [NET_BIND_SERVICE]
  readOnlyRootFilesystem: true
  runAsGroup: 0
  runAsNonRoot: false
  runAsUser: 0
podSecurityContext:
  fsGroup: 0
```

Then, create a file `ovh-application-credentials.secret.yaml` with your OVH credentials:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ovh-application-credentials
type: Opaque
data:
  OVH_APPLICATION_KEY: <base64 application key>
  OVH_APPLICATION_SECRET: <base64 application secret>
  OVH_CONSUMER_KEY: <base64 consumer key>
  OVH_ENDPOINT: <base64 endpoint>
```

And then apply it on the cluster: `kubectl apply -n traefik -f ovh-application-credentials.secret.yaml`.

:bulb: For other DNS providers (Azure, Gandi, Google Cloud DNS...), please refer to the following list to populate your secret files containing the credentials: [https://doc.traefik.io/traefik/https/acme/#providers](https://doc.traefik.io/traefik/https/acme/#providers).

You can finally install traefik with this command: `helm install -n traefik traefik traefik/traefik -f values.yaml`. A new replica set must have been created.

## Usage

To use the freshly installed Traefik on deployments, the following annotation must be present on Helm charts values file:

```yaml
ingress:
  annotations:
    kubernetes.io/ingress.class: traefik
```
