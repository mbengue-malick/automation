---
sidebar_position: 2
title: Git Workflow
---

In order for all the teams to understand everyone's repository workflow, it is _recommended_ to follow the Git Flow workflow. It is described as shown below:

![Integration process](/img/confiance_env/git_workflow.png)

It consists or four main branches or kinds of branches:

- `master` branch: depicts the state of production code
- `release` branches: depicts the pre-production version of the component
- `develop` branch: depicts the current working state of the component
- `feature` or `feat` branches: depicts the new feature/fix/refactor being worked on

To trigger pipelines and to set a version, tags must be used. The `-dev` and `-rc` tags will trigger snapshot builds whereas production tags (without suffix) will trigger production builds which can be used in a production environment.

Merge Requests (MR) can also be used to make code reviews easier.
