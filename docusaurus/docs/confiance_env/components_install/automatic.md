---
title: Automatic
sidebar_position: 2
---

## Requirements

This documentation covers the Continuous Deployment of Confiance components on a Kubernetes cluster. To install the components, it is required to follow the [cluster installation guide](/cluster/installation/intro.md) if a cluster installation is needed, and the [Gitlab runner guide](/cluster/cicd/gitlab_runner.md).

Each component is delivered with a Helm package, which values must be configured following your environment needs.

## Ansible Playbooks

The full documentation to run the deployment pipeline can be found [in this page](/cluster/cicd/ansible.md#pipeline) or in the `ansible-playbooks` repository.

### How does it work?

The Ansible playbooks are called through the `.gitlab-ci.yml` file located at the root of the project. They are launched by referencing the playbook's name and an inventory, depending on the environment chosen at the pipeline launch.

One of the first step of the playbooks is the clone of a repository called `chart-values-sub`, containing all the git submodules linked to chart project. Each project contains values files (`values.yaml` and `values.template.yaml.j2`): the template file picks its values on the `ansible-playbooks` repository, based on the Ansible variables and templating module. Then, the playbook will deploy the Helm Charts that have been packaged and pushed into a repository (Harbor in the present case).

Therefore, in order for the changes in a values file of the component to take effect in the cluster through an automated deployment, the `chart-values-sub` repository is always updated over the master branch of each chart repository.

### Examples

#### Example #1

I changed some template in the repository airflow-chart and successfuly tested it in a development namespace. I merged my developments to master and tagged them so a new package was pushed by Gitlab in Harbor. I also could have done it manually:

```bash
helm package ./
```

I can finally deploy the chart on the namespace v1 by launching the Ansible pipeline with the following parameters, from the `CI/CD > Pipelines` tab on Gitlab.

```bash
CLUSTER_ENVIRONMENT -> v1
DEPLOY_COMPONENTS -> true
CHART_AIRFLOW -> true
```

#### Example #2

I want to deploy all the components (which corresponding Helm Charts have already been pushed to a registry) on a brand-new cluster. The project has been added as a git submodule in `chart-values-sub` repository and the corresponding values of the template file have been updated in the `ansible-playbooks` repository by sending a merge request. I shall launch the Ansible pipeline with the following parameters:

```bash
CLUSTER_ENVIRONMENT -> prod
DEPLOY_COMPONENTS -> true
DEPLOY_KEYCLOAK -> true
DEPLOY_DASHBOARD -> true
ALL_CHARTS -> true
```
