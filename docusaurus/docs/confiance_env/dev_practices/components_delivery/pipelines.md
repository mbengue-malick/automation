---
sidebar_position: 1
title: Pipelines
---

Continuous Integration is set in the Confiance environment using Gitlab CICD pipelines. Some template pipelines have been developed on this [gitlab-ci-pipelines repository](https://git.irt-systemx.fr/confianceai/ec_1/fa2_infrastructure/gitlab-ci-pipelines), please feel free to elaborate new ones if needed and send a merge request to the maintainers. The actual continuous integration is meant to work following the [Git Flow](../git_flow.md).

## Template pipelines

Pipelines currently available on this repository:

- [Docker build](./docker.md): build a docker image following the `Dockerfile` on the project and push it to Harbor or Nexus.
- [Python build](./python.md): build a python lib following the `setup.py` file on the project and push it to Nexus
- [Helm chart package](/cluster/cicd/helm_docker.md): Package a Helm chart and push it to Harbor

## Set it on a new project

To set continuous integration on a new project, these steps have to be followed:

- Create a new file called .gitlab-ci.yml at the root of your project
- Develop your own pipeline or **use a template one** by doing the following:

```yaml
include:
  - project: "confianceai/ec_1/fa2_infrastructure/gitlab-ci-pipelines"
    ref: master
    file: "<filename>.gitlab-ci.yml"
```

- Commit your changes
- Make sure the Shared Runners are **disabled** and the Group Runners **enabled** by going to `Settings > CI/CD > Runners` on your Gitlab project interface.

![Gitlab Runner project Settings](/img/confiance_env/shared-runner.PNG)
![Gitlab Runner project Settings](/img/confiance_env/group-runner.PNG)

Set the following environment variables as masked variables (this is already done over the EC_1 group repository and therefore inherited by all the children repositories) by going to `Settings > CI/CD > Variables` on your Gitlab project interface:

```yaml
HARBOR_USER: user having rights to push to the desired Harbor repository (if it is a robot user, please do not type in robot$ at the beginning)
HARBOR_PWD: password or token associated to the above user
```

:::info
_Pro tip_: you can create a tag to verify the pipeline works as intended and delete it from the Gitlab interface if it is not needed.
:::

## Customize pipeline

To add, remove or customize pipeline stages, you can include the base pipeline depending your needs and then, for example, add some stages and then override the stages definition as follows:

```yaml
include:
  - project: "confianceai/ec_1/fa2_infrastructure/gitlab-ci-pipelines"
    ref: master
    file: "<filename>.gitlab-ci.yml"

stages:
  - build_snapshot # From the base pipeline
  - test # Custom stage
  - build_release # From the base pipeline
  - publish_elsewhere # Custom stage

before_script:
  - npm --version

test:
  stage: test
  script:
    - npm run test
    - echo "Successful testing"

publish:
  stage: publish_elsewhere
  script:
    - fly_me_to_the_moon.sh
```
