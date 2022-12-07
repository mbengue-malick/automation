---
title: Manual
sidebar_position: 1
---

## Requirement

This guide covers the manual deployment of Confiance components on a Kubernetes cluster.

On the kubernetes cluster:

- Create 5 Namespaces:
  - One for the components (`confiance` in this documentation)
  - One for the authentication components, if Keycloack is needed (`confiance-auth` in this documentation)
  - One for the components' Gatekeepers (`gatekeeper` in this documentation)
  - One for the monitoring tools
- Create secret for Docker Registry with account service, name for secret : regcred

Each component is delivered with a Helm package.

To deploy the most recent version, you can rely on the master branches of the repositories. 

:::caution Warning
Currently the chart helm repo of each component is composed of 2 values files:
- values.yaml
- values.template.yaml.j2

The last one is a values file that is populated by ansible variables during automatic deployment.
To be able to deploy manually, you will have to remove the .j2 at the end of the file and manually fill the variables with your value in this file.
Then when deploying the chart helm manually you will have to specify these two values files: ```-f values.yaml -f values.template.yaml ```
:::

## Infra and MLops tools deployment

### Keycloak

The repository used is [Bitnami](https://github.com/bitnami/charts/tree/master/bitnami/keycloak) in version 5.0.7. It should be installed with a custom value file.

Clone our repository to collect our values files (you must then adapt the values to your environment) : https://git.irt-systemx.fr/confianceai/ec_1/fa2_components/keycloak-chart



```bash
helm repo add bitnami https://charts.bitnami.com/bitnami # Add Bitnami repository
helm install keycloak bitnami/keycloak -f values.yaml -f values.template.yaml --namespace confiance-auth # Install the chart
```

Once the installation is done, Keycloak must be configured with the Active Directory :

The configuration is done by creating a new entry in __User Federation__ by choosing __ldap__.
The configuration of the AD in keycloak is facilitated by the default configuration by selecting __Active Directory__ in __Vendor__.


![keycloak AD](/img/confiance_env/conf_keycloak_AD.png)

For each component, in order to allow access through keycloack, it will be necessary to add in keycloack UI a client-id with their own configuration (mapper etc) for each component to deploy.

:::info
To import realms from a JSON file, it is needed to activate the "upload scripts" configuration in the values file. But be careful, this feature will soon be removed from newer versions of Keycloak.
:::

### JupyterHub

- Clone the custom Jupyterhub chart repository: [https://git.irt-systemx.fr/confianceai/ec_1/infra/jupyterhub-helm-chart](https://git.irt-systemx.fr/confianceai/ec_1/infra/jupyterhub-helm-chart).
- Create a client-id for jupyterhub in keycloack (you will have to add the keycloack secret for jupyterhub client-id)
- We use a custom docker image for the notebook instance, clone this repository and push this docker image in your artefact repository : [https://git.irt-systemx.fr/confianceai/ec_1/fa2_dockers/docker-systemx-notebook](https://git.irt-systemx.fr/confianceai/ec_1/fa2_dockers/docker-systemx-notebook).
- Remove the .j2 at the end of the file __values.template.yaml.j2__ and manually fill the variables with your own values (ingress host, keycloack client-id etc)


```bash
helm install jupyterhub ./ -f values.yaml -f values.template.yaml --namespace confiance # Install the chart
```

### AirFlow

We deploy Airflow by using the official Apache community chart: [https://github.com/apache/airflow/tree/main/chart](https://github.com/apache/airflow/tree/main/chart).

#### Requirements

- Airflow uses Fernet to encrypt passwords in the connection configuration and the variable configuration. It guarantees that a password encrypted using it cannot be manipulated or read without the key. Generate your own Fernet key using the following Python code snippet:

  ```python
  from cryptography.fernet import Fernet

  fernet_key= Fernet.generate_key()
  print(fernet_key.decode()) # your fernet_key, keep it in secured place!
  ```

- Airflow also uses a webserver secret created as follows:

  ```bash
  kubectl create secret generic airflow-webserver-secret --from-literal="webserver-secret=$(python3 -c 'import secrets; print(secrets.token_hex(16))')"
  ```

- To be able to use gitSync, to checkout DAGs from Gitlab every 60 sec, we created a token on Gitlab wich we passed as a chart value to the git link (as the values are stored in a vault they are secured), see l.95 dags from `values.yaml.j2`. The proper way to deploy is using a secret and passing it to the values, but it does not work with our configuration so we sticked to the token. In order to use the secret, you have to create a kubernetes secret containing an `id_rsa` key and add `id_rsa.pub` to your Gitlab instance:

  ```yaml
  apiVersion: v1
  kind: Secret
  metadata:
    name: airflow-git-ssh-creds
  type: Opaque
  data:
    id_rsa: <encoded id_rsa to base64>
  ```

  Or simply run this command: `kubectl create secret generic airflow-git-ssh-creds --from-file=./id_rsa` and then pass this secret to the values: credentialsSecret l.109 from `values.yaml.j2`.

- The service account used by airflow has a default cluster role in the `confiance` namespace to be able to instantiate workers and pods etc. (it can be used in multi-namespace mode l.1581 of `values.yaml` but it is forbidden here).

- Authentication (Oauth custom). This is a tricky part of the deployment: Airflow authentification is built on FAB (https://flask-appbuilder.readthedocs.io/en/latest/), Airflow versions are upgraded according to fab versions. In Confiance (as of 03/06/2022), we have deployed Airflow 2.2.4 (FAB 3.3.4) and had to override the FAB SecurityManager. To do so, you can either create a custom image of Airflow (with a custom `manager.py` script) or you can manually override the manager with the webserverconfig value (see `values.yaml.j2` l.9 webserverconfig). Inspired by [this article](https://awslife.medium.com/airflow-authentication-with-rbac-and-keycloak-2c34d2012059).

  In this code snippet, you define Keycloak as a custom OAuth provider as fab is built for standard providers such as github, twitter, linkedin, google, azure or openshift.

  If you are using Keycloak, you need to correctly configure the custom provider as follows:

  - Configuring Keycloak

    You will need:

    - A client id
    - Groups defined according to needs (Admin, Op, User, Viewer)

    Add a user to a specific group in `Users/name.surname/Groups`, this user will then be granted the privilege of the group (as groups are mapped to roles)

    You can also give him the role in role mapping directly but it’s more straightforward to use groups (`Users/name.surname/RoleMappings/client` roles: airflow-official-client to assign the desired role).

  - Configuring Airflow

    Described in the code snippet in `values.yaml.j2` l.9

#### Deployment

- Clone the [chart repository](https://git.irt-systemx.fr/confianceai/ec_1/fa2_components/airflow-official-chart.git).
- Remove the .j2 at the end of the file __values.template.yaml.j2__ and edit this file with your own information (fernetKey, resources, openid or other idp, ingress...)

```bash
helm repo add apache-airflow https://airflow.apache.org
helm update
helm install airflow apache-airflow/airflow -n confiance --version " 1.5.0" -f values.yaml -f values.template.yaml
```

- Make sure the groups are correct when you log in.

### MLflow

There are 3 components to deploy in order to have a remote mlflow (PostgreSQL, minIO, MLflow remote server).

A custom helm chart is made to deploy all components.

- Pull the [custom chart repository](https://git.irt-systemx.fr/confianceai/ec_1/infra/mlflow-chart.git).
- You need to create on Keycloack the authentication information to fill in values file for mlflow server and minIO.

#### Keycloack configuration for MLflow server 
On the keycloak UI, as an administrator, you have to create a client in the Clients menu by specifying the Client ID that will be used by values file.
![keycloak mlflow client](/img/confiance_env/mlflow_keycloak_clients_create.JPG)

Define all highlighted parameters in the image below:
![keycloak mlflow client settings](/img/confiance_env/mlflow_keycloak_clients_settings.jpeg)

Now you have to define a scope for the client. To do this, go to the Client Scopes menu and click on Create. Put its name here mlflow-scope :
![keycloak mlflow scope](/img/confiance_env/mlflow_client_scopes-create.jpeg)

In the Mappers create a new account value entry by pressing the Create button and select the right type in Mapper Type to Audience.
![keycloak mlflow mappers](/img/confiance_env/mlflow_client_scopes_mappers.jpeg)

Nothing to put in the scope.

After creating the client_scopes, you have to add it to the application. To do this, go to the application configuration, in the Client Scopes menu, and add the Assigned Dafaut Client Scopes to the client_scopes that has just been created. Here mlflow-scope :
![keycloak mlflow add scope](/img/confiance_env/mlflow_keycloak_clients_client_scopes.jpeg)

The credentials are retrievable on the Credentials tab and will be used for the configuration of the values file.

#### Keycloack configuration for minIO

On keycloak UI, as an admin user, create a client in Clients section. Specify the Client ID with minio,  which will be use in MinIO configuration.
![keycloak minio client](/img/confiance_env/minio_keycloack_client_setting.JPG)

Collect Client credentials in Credentials tab.

Create a mapper in Client section, in Mappers Tab :
![keycloak minio mapper](/img/confiance_env/minio_keycloack_client_mappers.JPG)

In UserFederation, create a new mapper policy with readwrite value for ldap-auth.irt-systemx.fr :
![keycloak minio policy](/img/confiance_env/minio_keycloack_user_federation_mapper.JPG)

In UserFederation, in ldap-auth.irt-systemx.fr settings, at the end click on 'Synchronize all users'.
Check if all openId scope are in Client Scope of minio client :
![keycloak minio conf ldap](/img/confiance_env/minio_openid_scope.JPG)

Add preferred_username,address,name,email in Client Scopes.
If one client scope is not available, you will need to create it on Client Scopes tab :
![keycloak minio scope](/img/confiance_env/minio_ScopeExample.JPG)


- Remove the .j2 at the end of the file __values.template.yaml.j2__ and edit this file with your own information (postgreSQL credentials, ingress...)
- Create a Kubernetes Secret file with your Minio credentials:

```yaml
---
apiVersion: v1
kind: Secret
metadata:
  name: mlflow-minio-keys
type: Opaque
stringData:
  access-key: <YOUR ACCESS KEY>
  secret-key: <YOUR SECRET KEY>
```

- Then apply it on the cluster: ```kubectl apply -f <SECRET FILE NAME>.yaml```

```bash
helm install mlflow . -n confiance -f values.yaml -f values.template.yaml
```

:::caution Warning
MLflow does not provide an authentication service, so we add our own proxy application in front to allow authentication with keycloack.
To do this, in the chart helm, the ingress must be set to false and it is the gatekeeper application for mlflow that opens the ingress following authentication on keycloack.
Refer to the section on gatekeeper deployment to set it up.
:::

### MinIO

- Clone the [repository](https://git.irt-systemx.fr/confianceai/ec_1/fa2_components/minio-chart.git).
- Create a secret file `minio_user_ecx_secret.yaml` with the minio credentials:
```yaml
---
apiVersion: v1
kind: Secret
metadata:
  name: minio-keys-ecx
type: Opaque
stringData:
  rootUser: <ROOT USERNAME>
  rootPassword: <ROOT PASSWORD>
```
- And apply it on the cluster with the following command `kubectl apply -f minio_user_ecx_secret.yaml`
- Remove the .j2 at the end of the file __values.template.yaml.j2__ and edit this file with your own information.
- Add the chart repository and install the chart
```bash
helm repo add minio https://charts.min.io/
helm install minio-storage minio/minio -n confiance -f values.yaml -f values.template.yaml
```

### Gatekeeper
Gatekeeper allows you to proxy applications by adding keycloack authentication to components that do not have the configuration to do it.

Regarding the gatekeeper, there is one generic chart helm and then one values file per component. It will be necessary to deploy.

- Clone the [Gatekeeper chart repository](https://git.irt-systemx.fr/confianceai/ec_1/infra/gatekeeper-chart.git)
- You need to create on Keycloack the authentication information to fill in values file :

On the keycloak UI, as an administrator, you have to create a client in the Clients menu by specifying the Client ID that will be used by __gatekeeper_deployment.yaml__.
![keycloak gatekeeper client](/img/confiance_env/keycloak_clients_create.jpeg)

Define all highlighted parameters in the image below :
![keycloak gatekeeper client conf](/img/confiance_env/keycloak_clients_settings.jpeg)

Now you have to define a scope for the client. To do this, go to the Client Scopes menu and click on Create. Put its name (Ex : pixano-scope).
![keycloak gatekeeper scope](/img/confiance_env/client_scopes-create.jpeg)

Make sure that Protocol and Include In Token Scope are set to the right value :
![keycloak gatekeeper scope settings](/img/confiance_env/client_scopes_settings.jpeg)

In the Mappers create a new account value entry by pressing the Create button and select the right type in Mapper Type to Audience : 
![keycloak gatekeeper mapper](/img/confiance_env/client_scopes_mappers.jpeg)

Make sure the Add to ID token and Add to access token settings are set to On
![keycloak gatekeeper mapper details](/img/confiance_env/client_scopes_mappers_details.jpeg)

Rien à mettre dans le scope.
![keycloak gatekeeper scope mapper](/img/confiance_env/client_scopes_mappers_scope.jpeg)

After creating the client_scopes, you have to add it to the application. To do this, go to the application configuration, in the Client Scopes menu, and add the Assigned Default Client Scopes to the client_scopes that has just been created. Here gatekeeper-scope (Ex : pixano-scope)
![keycloak gatekeeper client scope](/img/confiance_env/keycloak_clients_client_scopes.jpeg)

The credentials are retrievable on the Credentials tab and will be used for the configuration of the values.yml of the Helm file.
![keycloak gatekeeper credentials](/img/confiance_env/keycloak_clients_credentials.jpeg)


- Remove the .j2 at the end of the file __values.template.yaml.j2__ and edit this file with your own information (Keycloack client-id, credential).

Example for pixano component : 

```bash
helm install auth-pixano . -n gatekeeper -f values.yaml -f values.template.yaml
```


## Confiance bricks deployment

### Pixano

Pixano is deployed with a Helm chart:

- Clone the [custom chart repository](https://git.irt-systemx.fr/confianceai/ec_1/infra/pixano-chart.git)
- Remove the .j2 at the end of the file __values.template.yaml.j2__ and edit this file with your own information (NFS Storage).

```bash
helm install pixano . -n confiance -f values.yaml -f values.template.yaml
```

- To connect to Pixano, use `admin:admin` and change the admin password. Then, add users.


### DebiAI

DebiAI is deployed with a Helm chart:

- Clone Clone the [custom chart repository](https://git.irt-systemx.fr/confianceai/ec_1/infra/debiai-chart.git)
- Remove the .j2 at the end of the file __values.template.yaml.j2__ and edit this file with your own information (NFS Storage).

```bash
helm install debiai . -n confiance -f values.yaml -f values.template.yaml
```

:::caution Warning
Unlike Pixano, DebiAI does not have authentication management. Therefore it is recommended to add the Gatekeeper chart in front of the application to protect its access.

To do this, in the chart helm, the ingress must be set to false and it is the gatekeeper application for debiai / pixano that opens the ingress following authentication on keycloack.
Refer to the section on gatekeeper deployment to set it up.
:::
