---
sidebar_position: 1
title: Gitlab Runner
---

[Official doc](https://git.irt-systemx.fr/help/user/project/clusters/add_remove_clusters.md)

The resources to deploy a runner and the Ansible executor image can be found in the [ansible-playbooks repository](https://git.irt-systemx.fr/confianceai/ec_1/fa2_infrastructure/ansible-playbooks/).

## Runner

Install the Runner by following this [official guide](https://docs.gitlab.com/runner/install/kubernetes-agent.html). Please take care to replace `gitlabUrl` with your Gitlab URL (`https://git.irt-systemx.fr` in the case of Confiance) and set a `runnerRegistrationToken` (found on your **group repository**, in Settings > CI/CD > Runners). The values to apply can be found in the file `values_gitlab_runner.yaml`. Put shortly, and with the values completed, here are the commands to launch:

```bash
helm repo add gitlab https://charts.gitlab.io
kubectl create namespace gitlab
helm install --namespace gitlab --name gitlab-runner -f ./values.yaml gitlab/gitlab-runner
```

To give rights to the runner on the whole cluster, apply the file `cluster_roles.yaml` (it also works to register the `gitlab-runner` Service Account on the `cluster-admin` Cluster Role Binding, but this latter is leading to a security misconfiguration):

```bash
kubectl apply -f cluster_roles.yaml
```

To upgrade the runner, launch:

```bash
helm upgrade -n gitlab gitlab-runner --set gitlabUrl=https://git.irt-systemx.fr,runnerRegistrationToken=<token> gitlab/gitlab-runner
# OR
helm upgrade -n gitlab gitlab-runner gitlab/gitlab-runner -f values_gitlab_runner.yaml
```

An other easy method to change the registration token is to modify directly the Kubernetes secret tied to the Gitlab Runner deployment and restart the pods:

```bash
# Edit the secret
kubectl edit secrets -n gitlab gitlab-runner
# "Restart" the pod
kubectl scale deployment -n gitlab gitlab-runner --replicas 0
kubectl scale deployment -n gitlab gitlab-runner --replicas 1
```

## Executors

### Ansible executor

The runner now needs an executor. In our case, we need to be able to execute Ansible playbooks. Build and push the Gitlab executor image (whose Dockerfile can be found in the [ansible-playbooks repository](https://git.irt-systemx.fr/confianceai/ec_1/fa2_infrastructure/ansible-playbooks/)) into a public registry (e.g. Harbor) so that it can be referenced as an executor in a `.gitlab-ci.yml` file:

```bash
docker build -t gitlab-executor:alpine-3.14 -f gitlab-executor.Dockerfile .
# Harbor repository
docker tag gitlab-executor:alpine-3.14 harbor.irtsysx.fr/confiance-infra/gitlab-executor:alpine-3.14
docker push harbor.irtsysx.fr/confiance-infra/gitlab-executor:alpine-3.14
```

### Docker in Docker

To build Docker images in the executor, it is necessary to use a Docker-in-Docker base image and configure it to share the Docker host socket as shown below. You can change the Docker image version and the TCP host according to your needs and your configuration.

```yaml
image: docker:20.10

variables:
  # See https://docs.gitlab.com/ee/ci/docker/using_docker_build.html#docker-in-docker-with-tls-enabled-in-kubernetes
  DOCKER_HOST: tcp://docker:2376
  DOCKER_TLS_CERTDIR: "/certs"
  DOCKER_TLS_VERIFY: 1
  DOCKER_CERT_PATH: "$DOCKER_TLS_CERTDIR/client"

services:
  - docker:20.10-dind
```

### Other executors

Other executors can be found in the [gitlab-ci-pipelines repository](https://git.irt-systemx.fr/confianceai/ec_1/fa2_infrastructure/gitlab-ci-pipelines) in the `Dockerfile` folder. The tag name is indicated on the first line of the Dockerfiles. For now, two executors are described: one for packaging Helm charts, and one for building Python libraries.

### Usage

To use a specific executor in your Gitlab CICD pipeline, specify the image in the `.gitlab-ci.yml` file, for example:

```yaml
# Image stored in Harbor
image: harbor.irtsysx.fr/confiance-infra/gitlab-executor:alpine-3.14

# Image stored in Docker Hub or any public repository
image: node:lts
```

## Configuration on Gitlab

If you deployed the runner **at a group level** (i.e. with a token taken in the group settings), you will be able to use it on every project on this group without taking further actions.

If you deployed the runner **at a repository level**, go to the project where you took the `runnerRegistrationToken` and go to Settings > CI/CD > Runners: you should see your runner up and... running. Click on the pen as shown in the image below.

![Pen button to edit a Gitlab runner](/img/cluster/cicd_gitlab_runner.png)

Then, unselect the property "Lock to current projects" as follows in order to make the runner useable in all your other projects:

![Unselect "Lock to current projects" property](/img/cluster/cicd_gitlab_runner_unlock.png)

In an other project which needs a runner, you only have to go to Settings > CI/CD > Runners and click on the "Enable for this project" button of the specific runner you want to use:

![Enable button for the runner](/img/cluster/cicd_gitlab_runner_enable.png)
