---
sidebar_position: 2
title: Use Cases data access
---

## NFS

Use Cases data is stored on an NFS server located on this address: `152.228.211.245` and is mounted on `/nfsdata`. The NFS has a 4TB size so everyone must be careful on its usage. Also, its integrity is in the hands of all the users.

:::info
If the NFS is full or if you cannot access it, please open a ticket on the dedicated Teams channel.
:::

## MinIO

Data can also be accessed through MinIO by using [the console](https://minio-storage-console.apps.confianceai-public.irtsysx.fr/), the Minio Client CLI, `mc`, or by using the `minio` library for Python (which also exists for Golang, .NET, Java and JavaScript). The console allows you to login via your IRT account, but to use `mc` or the `minio` library, you will need to generate a service account. MinIO is set up with buckets, one for each Use Case, following [access policies](/cluster/management/minio) allowing you to browse all the files on your accessible buckets, and write/delete files only on the `Resultats_projets` folder of each bucket.

### Service Account

To create one or several service accounts, login to [the console](https://minio-storage-console.apps.confianceai-public.irtsysx.fr/) and go to the Service Accounts menu:

![MinIO Service Accounts menu](/img/confiance_env/data_access_minio_sa.png)

Then, click on `Create service account` and on `Create` again. Write down the generated Secret Key as you will not be able to retrieve it after the window closes.

### MinIO Client `mc`

MinIO Client can be installed and configured following [the official documentation](https://min.io/docs/minio/linux/reference/minio-mc.html). To use `mc` to operate on your buckets, you first have to set an alias to store your credentials:

```bash
mc alias set ALIAS HOSTNAME ACCESS_KEY SECRET_KEY
# Example
mc alias set minio https://minio-storage.apps.confianceai-public.irtsysx.fr qs6ef84qefafd5f4 48azd6a4-a65sd4a-sd54
# Try the connection
mc ls minio
```

### Python

To use MinIO in your Python code, you can follow [the official documentation](https://min.io/docs/minio/linux/developers/python/minio-py.html). For example, you can set you ACCESS_KEY and SECRET_KEY as environment variables not to expose it directly in your code and to make it easier to build your code on Gitlab CI/CD or use it in an Airflow DAG:

```python
from minio import Minio
import os

client = Minio(
    "minio-storage.apps.confianceai-public.irtsysx.fr",
    access_key=os.environ.get('MINIO_ACCESS_KEY'),
    secret_key=os.environ.get('MINIO_SECRET_KEY'),
)

client.bucket_exists("use-cases")
```
