---
title: Nexus
---

Nexus allow to host this artefacts :

- Python repository :
    - pypi-snapshots (dev and integration)
    - pypi-releases (prod)
- Docker repository :
    - docker-private 

Nexus Link : https://repo.irtsysx.fr

You can visit this [link](https://docs.apps.confianceai-public.irtsysx.fr/confiance_env/components/jupyterhub#configure-access-to-nexus) to learn how to configure your Jupyter instance to pull python librairies from the Nexus.

Gitlab-ci pipeline are available to automate delivery in Nexus.