---
sidebar_position: 8
title: Keycloak
---

In order to connect the cluster to Keycloak, we first need to create a client on the latter. We assume that there is already a client created for the other clusters (internal and public). We use this same client for the new cluster.

Here is the information needed:

```yaml
realm_url: https://keycloak.irtsysx.fr/auth/realms/smite
token_url: https://keycloak.irtsysx.fr/auth/realms/smite/protocol/openid-connect/token
```

Once the client has been created on Keycloak, let's configure the cluster. On the masters, edit the API-Server manifest which is located in `/etc/kubernetes/manifests`

```bash
sudo vi /etc/kubernetes/manifests/kube-apiserver.yaml
```

In the list of commands, add the Keycloak configurations:

```bash
- --oidc-client-id=kubernetes
- --oidc-groups-claim=groups
- --oidc-issuer-url=https://keycloak.irtsysx.fr/auth/realms/smite
- --oidc-username-claim=preferred_username
- --oidc-username-prefix=-
```

The cluster is now connected to the keycloak. To allow users to authenticate with their AD username, edit in [this repository](https://git.irt-systemx.fr/confianceai/ec_1/fa2_infrastructure/kubectl-config) the file `config.yaml` to add the new cluster.

```bash
cluster:
  public-v2:
    client_secret: <client-secret>
    realm_url: https://keycloak.irtsysx.fr/auth/realms/smite
    token_url: https://keycloak.irtsysx.fr/auth/realms/smite/protocol/openid-connect/token
username: {{username}}
```

In the same repository, edit the config file to add the new context:

```bash
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: <server-certificate>
    server: <cluster-url>
  name: public-v2
contexts:
- context:
    cluster: public-v2
    user: public-v2-{{username}}
  name: public-v2
users:
- name: public-v2-{{username}}
  user:
    auth-provider:
      config:
        client-id: kubernetes
        client-secret: <client-secret>
        id-token: <id-token>
        idp-issuer-url: https://keycloak.irtsysx.fr/auth/realms/smite
        refresh-token: <refresh-token>
      name: oidc
```

Rerun the script .sh in this repository to take into account the new cluster and when finished, test with: `kubectl login public-v2`.
