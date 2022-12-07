---
sidebar_position: 2
title: Helm and Docker
---

When considering CI CD on the cluster, different objects are taken into account:

- Helm charts: packaged and pushed (CI), and deployed on preprod environment (CD)
- Docker images of web apps: built and pushed (CI), and deployed on prod environment (CD)

## Charts and Images location

| Component         | Image                                           | Chart                      |
| ----------------- | ----------------------------------------------- | -------------------------- |
| Airflow           | Docker Hub: apache/airflow                      | airflow.apache.org         |
| DebiAI            | Harbor IRT: ml/debiai/debiai-backend-py         | Harbor IRT                 |
| Docusaurus        | Nexus Confiance: confiance/docusaurus           | Harbor IRT                 |
| Gatekeeper        | Quay.io: gogatekeeper/gatekeeper                | Harbor IRT                 |
| Jupyterhub        | Docker Hub: jupyterhub/k8s-hub                  | Harbor IRT                 |
| Jupyterhub - Base | Nexus Confiance: confiance/datascience-notebook | N/A                        |
| Keycloak          | Docker Hub: bitnami/keycloak                    | charts.bitnami.com/bitnami |
| MinIO             | Quay.io: minio/minio                            | charts.min.io              |
| MLflow            | Nexus Confiance: confiance/mlflow-server        | Harbor IRT                 |
| OpenSearch        | Docker Hub: opensearchproject/opensearch        | Harbor IRT                 |
| Pixano            | Docker Hub: pixano/pixano-app                   | Harbor IRT                 |

## Helm charts

All the Confiance Helm charts are located in the subgroup [FA2_Components](https://git.irt-systemx.fr/confianceai/ec_1/fa2_components/). The repositories contain:

- The definition of the Helm chart if it is a custom one (`Chart.yml`, `templates/`...)
- The `values.yaml` file defining global values for the chart
- The `values.template.yaml.j2` file, which is used by Ansible to define environment-dependent variables
- The `.gitlab-ci.yml` where the CI is defined

### Values files

Chart values are defined in two files: `values.yaml` and `values.template.yaml.j2`. The first one is used to define **global values**, such as pod configuration, probes, service, containers... To generate a values file from an existing chart, launch `helm show values <my-repo>/<my-chart>`. The second one is a Jinja2 templated file, used to store values dependent over an environment: host, resources, passwords...

Here is an example of templated values:

```jinja
volumes:
  - name: data
    nfs:
      server: {{ values_nfs_server }}
      path: {{ values_nfs_path }}
ingress:
  enabled: true
  host: {{ values_host }}
```

During the deployment (explained later), Ansible will replace the variables between double braces `{{ }}` by their values defined in the inventories. Also, as this values file is called after the `values.yaml` in the Ansible playbook during the helm upgrade/install step, values defined here will override the ones in `values.yaml`.

:::info local development
For _local development_, the `values.template.yaml.j2` can be templated with an ansible pipeline found [here](https://git.irt-systemx.fr/confianceai/ec_1/fa2_infrastructure/ansible-playbooks/-/pipelines) with the following parameters:

```yaml
CLUSTER_ENVIRONMENT: <deployment-env>
TEMPLATE_VALUES: <name-of-the-chart>

# Example
CLUSTER_ENVIRONMENT: preprod
TEMPLATE_VALUES: jupyterhub-chart
```

:::

### Gitlab CI file

The `.gitlab-ci.yml` is the same for all the Helm charts:

```yaml
include:
  - project: "confianceai/ec_1/fa2_infrastructure/gitlab-ci-pipelines"
    ref: master
    file: "helm-chart-package.gitlab-ci.yml"
```

It consists of a link towards an other pipeline definition, `helm-chart-package.gitlab-ci.yml` defining the below steps which are only launched on the following condition: a tag is set on the chart's repository in the _semver format_. Example: `1.0.0`, `03.20.09`, `1.0.0-dev`, `01.01.01-rc`. The pipeline is found on the [gitlab-ci-pipelines repository](https://git.irt-systemx.fr/confianceai/ec_1/fa2_infrastructure/gitlab-ci-pipelines).

- Package of the chart, tagged from the git tag version, and pushed to [Harbor](https://harbor.irtsysx.fr/)
- Deployment of the chart to the `preprod` namespace on the cluster

The pipeline is customizable by overriding the following variables at the top of the `.gitlab-ci.yml` file on the chart repository:

```yaml
# These are the default values
variables:
  PROJECT_VERSION: "$CI_COMMIT_TAG" #set the version on the chart to this semver version
  APP_VERSION: "" #set the appVersion on the chart to this version
  DEPLOY_CHART: "true" #deploy the chart to the cluster
  ANSIBLE_ENV_VAR: "" #chart env var, example: CHART_JUPYTERHUB, CHART_OPENSEARCH, CHART_PIXANO... cf ansible-playbooks repository
```

### Chart values submodules repository

All the Helm charts repositories are centralized in a parent repository: [chart-values-sub](https://git.irt-systemx.fr/confianceai/ec_1/fa2_components/chart-values-sub). The repositories are added as Git submodules (cf [official documentation](https://git-scm.com/book/en/v2/Git-Tools-Submodules)), acting as links to the repos.

This repositories has been created for Ansible playbooks in order for them to access all the values and the templates files inherent to the charts easily.

:thought_balloon: Please remember that **every new chart must be added in this repository** to be deployable with the Gitlab pipeline.

### Ansible pipeline

> A more documented section about Ansible, its usage and the playbook development workflow can be found [here](./ansible.md).

The deployment pipelines are defined on [this repository](https://git.irt-systemx.fr/confianceai/ec_1/fa2_infrastructure/ansible-playbooks). The deployment of Helm charts is defined in the `install_components.yml` playbook. It contains these steps:

- Creation of the wanted namespace, if applicable. Dependent of the environment (prod, preprod...) defined in the pipeline
- Git clone of chart-values-sub
- Values files Jinja templating
- Deployment of the component(s) chart(s)
- Deployment of the gatekeeper(s), if applicable

To launch a pipeline, go to [the pipeline section](https://git.irt-systemx.fr/confianceai/ec_1/fa2_infrastructure/ansible-playbooks/-/pipelines) of the ansible-playbooks repository and add some parameters depending on your needs. The list of all the available parameters is described in the ansible-playbooks repository's `README.md`.
For example, to deploy Jupyterhub on the prod namespace, add the following parameters:

```yaml
CLUSTER_ENVIRONMENT: prod
DEPLOY_COMPONENTS: true
CHART_JUPYTERHUB: true
```

## Docker - Web Apps

Web applications built by EC1, located [in this repository](https://git.irt-systemx.fr/confianceai/ec_1/fa2_webapps) have dedicated Dockerfile and `.gitlab-ci.yml` files. They are not mutualized but the steps follow the same pattern:

- Build and push step: on tag or push to master, build the Docker image following the Dockerfile and push it to Harbor
- Trigger CD step: on tag or push to master, trigger the `ansible-playbook` pipeline by executing the dedicated playbook. The playbooks consist of the creation of a chosen namespace, if applicable, and the deployment of the Helm chart.

For other Docker images, please read the [Development Practices dedicated chapter](/confiance_env/dev_practices/components_delivery/docker.md).
