---
sidebar_position: 1
title: Global presentation 
---

Confiance.AI components can be accessed through the [Home Dashboard](https://home.apps.confianceai-public.irtsysx.fr/). Here is a list of the major tools used in the environment :

- [Airflow](./airflow.md) : Airflow is a platform to programmatically author, schedule and monitor workflows.
- [DebiAI](./debiai.md) : DebiAI aims to facilitate the development of Machine Learning models, especially in the stage of data visualization and data analysis.
- [Docusaurus](./docusaurus.md) : Technical documentation, Markdown based.
- [Gitlab](./gitlab.md) : Store and review your source code in a secure environment.
- [Jupyterhub](./jupyterhub.md) : A multi-user version of the notebook IDE designed for companies and research labs.
- [MinIO](./minio.md) : MinIO is a High Performance Object Storage. It can handle unstructured data such as photos, videos...
- [MLflow](./mlflow.md) : MLflow is an open source platform for managing the end-to-end machine learning lifecycle.
- [Nexus](./nexus.md) : Nexus is a repository management platform, allowing to host artefacts.
- [OpenSearch](./opensearch.md) : OpenSearch is a community-driven, open source fork of Elasticsearch and Kibana following the licence change in early 2021.
- [Pixano](./pixano.md) : Pixano provides a set of re-usable components to build customizable image and video annotation tools.

All components are available with a Keycloack authentication with your IRT-SytemX credentials.


**The specifications for V1.1 :**

Cluster Kubernetes on OVH : v1.23.6
- 3 masters
    - 2 CPU
    - 7 Go RAM
- 4 workers CPU
    - 16 CPU
    - 60 Go RAM
- 2 workers GPU
    - 56 CPU
    - 180 Go RAM
    - 4×Tesla V100S 32 Go

Storage : 
- Personal Storage (PVC) link to JupyterHub Instance : 10Gi for each user (can be extend)
- hared Storage NFS : 4To
- MinIO : global S3 Storage for Confiance.AI


All these components are deployed mainly on a Kubernetes cluster. You can find all the technical information about the cluster in section [Cluster](/cluster/intro.md) 

