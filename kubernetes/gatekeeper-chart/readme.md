# Installation d'un client de keycloak

L'objectif de la documentation est d'installation d'un proxy-auth d'un application sur keycloak avec gogatekeeper.
Cette documentation n'est pas là pour expliquer l'installation de keycloak, il faut pour cela voir [keycloak-chart](https://git.irt-systemx.fr/confianceai/ec_1/infra/keycloak-chart).


Mode opératoire :

Créer un fichier yaml de la configuration de l'application où il faut poser le proxy-auth. Il faut paramètrerl'url de keycloak, l'url de l'application avec son __fqdn interne à kubenetes__.

~~~yaml
keycloak:
  # Url d'accès à keycloak : https://<fqdn de keycloak>/auth/realms/<nom du realm>
  keycloakUrl: https://keycloak.confiance.irtsysx.fr/auth/realms/confianceai
  # Nom du "Client Id", voir https://git.irt-systemx.fr/mickael.patron1/monapp/-/blob/master/keycloak_configuration.md
  clientId: pixano-id
  # Valeur du password, voir les crédentials dans https://git.irt-systemx.fr/mickael.patron1/monapp/-/blob/master/keycloak_configuration.md
  clientSecret: b5eb73b6-48bf-45fb-9556-3a418aac448c
  # Les mots de passe du l'application pour la communication avec keycloak. Y mettre une valeur random.
  # exemple : tr -dc A-Za-z0-9 </dev/urandom | head -c 32 ; echo ''
  encryptionKey: Xa6LaeNIwEcvT1SegCRuo7ZVEbcikh2J
  # upstream-url=http://{{ .Chart.Name }}.{{ .Release.Namespace }}.svc.cluster.local:{{ .Values.service.port }}
  upstreamUrl: http://pixano-chart.confiance.svc.cluster.local:3000

~~~

Puis lancer les commandes suivantes :

~~~bash
kubectl login confianceai-public
helm install auth-debiai . --namespace gatekeeper --values ./values_debiai.yaml
helm install auth-debiai-backend . --namespace gatekeeper --values values_debiai-backend.yaml
helm install auth-mlflow . --namespace gatekeeper --values ./values_mlflow.yaml
helm install auth-pixano . --namespace gatekeeper --values ./values_pixano.yaml
helm list -n gatekeeper
kubectl get -n gatekeeper pods
helm uninstall debiai-backend -n gatekeeper && watch kubectl get -n gatekeeper pods
helm uninstall debiai -n gatekeeper && watch kubectl get -n gatekeeper pods
kubectl get -n gatekeeper pods,services,ingress
~~~

## Documentation de la configuration à poser dans keycloak

Documentation pour la mettre en place l'authentification de l'application sur keycloak
___[Configuration de keycloak pour l'intégration de l'application](keycloak_configuration.md)___

Source : https://github.com/gogatekeeper/gatekeeper/blob/master/docs/user-guide.md
