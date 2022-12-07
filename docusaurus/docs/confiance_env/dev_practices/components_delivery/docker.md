---
sidebar_position: 2
title: Docker Images Pipeline
---

## Gitlab CI file

The delivery of Docker images consists of a link towards an other pipeline definition, `docker-build.gitlab-ci.yml` defining the below steps which are only launched on the following condition: a tag is set on the chart's repository in the _semver format_. Example: `1.0.0`, `03.20.09`, `1.0.0-dev`, `01.01.01-rc`. The pipeline is found on the [gitlab-ci-pipelines repository](https://git.irt-systemx.fr/confianceai/ec_1/fa2_infrastructure/gitlab-ci-pipelines).

- Build of the image, tagged from the git tag version and `latest`
- Push to [Harbor](https://harbor.irtsysx.fr/) or [Nexus](https://repo.irtsysx.fr/)

To use it on your Dockerized projects, use the following `.gitlab-ci.yml` file:

```yaml
include:
  - project: "confianceai/ec_1/fa2_infrastructure/gitlab-ci-pipelines"
    ref: master
    file: "docker-build.gitlab-ci.yml" # Push to Harbor
    #file: 'docker-build-nexus.gitlab-ci.yml' # Push to Nexus
```

The pipeline is customizable by overriding the following variables at the top of the `.gitlab-ci.yml` file on your repository:

```yaml
# These are the default values
variables:
  PROJECT_NAME: "$CI_PROJECT_NAME" #set the name on the image to this string
  PROJECT_VERSION: "$CI_COMMIT_TAG" #set the version on the image to this semver version
  PROJECT_DOCKERFILE: "./Dockerfile" #set the Dockerfile name/location
```

Example of a customized pipeline:

```yaml
variables:
  PROJECT_DOCKERFILE: "./ci_cd/my-dockerfile"

include:
  - project: "confianceai/ec_1/fa2_infrastructure/gitlab-ci-pipelines"
    ref: master
    file: "docker-build.gitlab-ci.yml"
```

:::caution Troubleshooting
If a `pip install` command returns a TimeOut error, please verify that your followed [these steps](./pipelines#set-it-on-a-new-project), and add this to your Dockerfile:

```bash
ARG USER_NEXUS
ARG PASSWORD_NEXUS

pip install -i https://$USER_NEXUS:$PASSWORD_NEXUS@repo.irtsysx.fr/repository/<your-repository> <your-package>
```

:::
