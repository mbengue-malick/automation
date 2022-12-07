---
sidebar_position: 3
title: Python Libs Pipeline
---

## Gitlab CI file

The delivery of Python libraries consists of a link towards an other pipeline definition, `python-lib-build.gitlab-ci.yml` defining the below steps which are only launched on the following condition: a tag is set on the chart's repository in the _semver format_. Example: `1.0.0`, `03.20.09`, `1.0.0-dev`, `01.01.01-rc`. The pipeline is found on the [gitlab-ci-pipelines repository](https://git.irt-systemx.fr/confianceai/ec_1/fa2_infrastructure/gitlab-ci-pipelines).

- Build the library following the `setup.py` file
- Push to [Nexus](https://repo.irtsysx.fr/)

To use it on your Python libs projects, use the following `.gitlab-ci.yml` file:

```yaml
include:
  - project: "confianceai/ec_1/fa2_infrastructure/gitlab-ci-pipelines"
    ref: master
    file: "python-lib-build.gitlab-ci.yml"
```

The pipeline is customizable by overriding the following variables at the top of the `.gitlab-ci.yml` file on your repository:

```yaml
# These are the default values
variables:
  PROJECT_NAME: "$CI_PROJECT_NAME" #set the name on the library to this string
  PROJECT_VERSION: "$CI_COMMIT_TAG" #set the version on the library to this semver version
  PROJECT_TYPE: "wheel" #set the project type: can be "wheel" or "egg" ("wheel" is recommended)
```

Example of a customized pipeline:

```yaml
variables:
  PROJECT_TYPE: "egg"

include:
  - project: "confianceai/ec_1/fa2_infrastructure/gitlab-ci-pipelines"
    ref: master
    file: "python-lib-build.gitlab-ci.yml"
```
