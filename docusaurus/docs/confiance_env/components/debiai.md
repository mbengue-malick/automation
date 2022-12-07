---
title: DebiAI
---

DEBIAI is a tool for data vizualization and analysis that can be applied for the analysis of both training, testing and predicted data.

DebiAI UI Link : https://debiai.apps.confianceai-public.irtsysx.fr/debiai

DebiAI comes with a keycloack authentication, so to be able to call the app backend in Jupyter (which are both components present in the same Kubernetes cluster) you have to use the internal Kubernetes route :

DEBIAI_BACKEND_URL = 'http://debiai.confiance.svc.cluster.local:3000/'

For more information on this tool, you may look at its [wiki page documentation](https://wiki.confiance.ai/wiki/DEBIAI)