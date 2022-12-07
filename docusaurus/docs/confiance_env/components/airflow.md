---
title: Airflow
---

Airflow allows to build and schedule pipeline from a DAG (Directed Acyclic Graph), which is the core concept of Airflow, it collecting Tasks together, organized with dependencies and relationships to say how they should run.

In the Confiance program, automatic tasks have been developped in order to easily use Airflow to launch existing code in docker containers. It's useful for executions which require a lot of ressources or long ones because Airflow is more flexible than other tools like Jupyter: you can customize your environment as you want and choose the ressources to use. The article explains how to do that. 

Airflow UI Link : https://airflow.apps.confianceai-public.irtsysx.fr

Airflow is synchronized with a git directory for retrieving all DAGs. Synchronisation is done every 60s on the master branch. So you can push, update the code of your DAG, and with the synchronization you can trigger your DAGs from the airflow UI (if the trigger is manual)
Git repository for airflow synchronization : https://git.irt-systemx.fr/confianceai/ec_1/infra/airflow-dags

On the same git repository, you can find several templates on the branch [templates](https://git.irt-systemx.fr/confianceai/ec_1/infra/airflow-dags/-/tree/templates)

## Overall functioning

To easily execute your code with airflow, we recommend that you do the following :

Create an airflow pipeline to run tasks in pods in the kubernetes cluster. Executing a task consists of specifying a docker image to deploy in the pod and the command to execute in it.

To do this you will need : 
1. Create a docker image that breaks down each task to be executed into scripts contained in the docker image (which means create the specifications of the docker image called Dockerfile).
2. Build and push this docker image on Nexus, the repository of docker images (a gitlab-ci pipeline is available to do this automatically)
3. Push on the repo git synchonized the code of the dag, which will detail each task by specifying the docker image to pull and the script to run
4. Run the pipeline on the UI.

In the dag it will be possible to add a connection to the NFS storage, to choose the resources to allocate to the task execution, read parameters entered at the start of the dag thanks to a configuration file, etc.

## Configure Nexus connexion 

To use the **KubernetesPodOperator** in your dag, which will deploy a docker container in a pod, you have to connect to the nexus repository to retrieve the images that have been pushed on it thanks to the **docker-build-nexus.gitlab-ci.yml** pipeline.

You must specify the path of the image and the secret that allows the pull from nexus, like this: 

```
 step = KubernetesPodOperator(
        [...]
        image="repo.irtsysx.fr:5086/confiance/<IMAGE_NAME>:<IMAGE_TAG>",   
        image_pull_secrets=[k8s.V1LocalObjectReference('secretnexus')],
        image_pull_policy='Always',
        [...]
 )

```


## Usage Example on Air Liquide TimeSeries UseCase
This example of using the different tools to produce a end to end ML pipeline is based on the air-liquide time series use case.


![Airflow example on Air Liquide UC](/img/confiance_env/airflow-airliquide-example.png)

Two airflow pipeline are created :

- Pipeline 1 : Building and save model
    - 3 tasks on the [DAG](https://git.irt-systemx.fr/confianceai/ec_1/infra/airflow-dags/-/blob/templates/pipeline_example_uc_airliquide_training.py)
        - Data Preparation : Load data, make preprocessings and store clean data on pod volume
        - Training : Use MLflow for track metadata's experiment
        - Prepare serving and make one static prediction for building png artefact with graph result
    
- Pipeline 2 : Model Serving
    - 3 tasks on the [DAG](https://git.irt-systemx.fr/confianceai/ec_1/infra/airflow-dags/-/blob/templates/pipeline_example_uc_airliquide_serving.py)
        - Serve model in Kubernetes Pod with MLflow serving (KubernetesPodOperator)
        - Create Kubernetes Service to expose the service app (PythonOperator)
        - Create Kubernetes Ingress to access to the app with URI (PythonOperator)


The airflow tasks are KubernetesPodOperator in order to launch a pod based on the docker image and to execute the commands of each task. The docker image is push on another [repository](https://git.irt-systemx.fr/confianceai/ec_1/infra/demo_airflow_uc_airliquide/-/tree/master)

After the model serving pipeline run, a pod on the cluster kubernetes will remain to expose the model through an API. You can call the API for prediction service :

curl -i https://serving-demo-airliquide.confiance.irtsystemx.org/invocations -H 'Content-Type: application/json; format=pandas-records' -d '[     {"Categorical_0_32702118b4932004c318a5aba2de206350a9d780":1.0,"Categorical_0_50065473ebf0081d30837c1cbe0f3636dffca153":0.0,"Categorical_0_5a969a185491600acc0f2a3d8816952fb093e681":0.0,"Categorical_0_91158be1505ed54294d25ca450c64dd163ab0a9a":0.0,"Categorical_0_a6a3993db10bfa2224af0e3895c00d09338be73e":0.0,"Categorical_0_abefb948a9897bb1d74756502c7e4263f00bc809":0.0,"Categorical_0_d06ba9afb09033eedb8b917f340845167a5b6f72":0.0,"Categorical_0_e3d7212362578b964f6fb7cda543574e5697a50e":0.0,"Categorical_0_fc0df94132e77a61f46c10dfa271a0d1e31ff26b":0.0,"Categorical_1_12b9e32c52b78b9a4ecce138a1049196a89bbfe6":1.0,"Categorical_1_2892926d19b202eee9cefa3f3599f3413d8cc34d":0.0,"Categorical_1_92821f8cf052972532de32487dc80d38efc87748":0.0,"Categorical_1_f72117bd17a93c040d0cf69a69ef8b81b3c2ff45":0.0,"Categorical_2_05c73964f4dff29d1c5b82e23c98258758337a26":1.0,"Categorical_2_36bebaf181b3a8a2c6d0e4aa97ed80ff76e0782f":0.0,"Ordered_categorical_0":6.0,"Ordered_categorical_1":39.0,"Ordered_categorical_2":0.0,"Ordered_categorical_3":0.0,"Numerical_3":-0.0926033291,"Numerical_0_2":-0.8183746868,"Numerical_0_3":-0.5754426411,"Numerical_0_4":-0.7135431329,"Numerical_0_5":-0.6375003428,"Numerical_1_2":-0.2476474743,"Numerical_1_3":-0.0298145793,"Numerical_1_4":-0.0661200618,"Numerical_1_5":0.0427963857,"Numerical_2_1":-0.7688669308} ]'

Link to the demo [video demo](https://irtsystemx.sharepoint.com/:v:/s/IAdeConfiance833/EUkaYhVRlNhNowPYYQlCFiEBNai8FM-2C8heVKh5GdeQOg?e=6S6klw)


## Templates NFS

[template_nfs.py](https://git.irt-systemx.fr/confianceai/ec_1/infra/airflow-dags/-/blob/templates/template_nfs.py) : DAG example with one task that deploy an Ubuntu Pod on Kubernetes Cluster, with a volume mount configuration on NFS server for the pod.

NFS configuration :
```
nfs_volume = V1Volume(
    name='nfs-volume',
    nfs=V1NFSVolumeSource(path='/nfsdata', server='152.228.211.245'))

## You will have access to NFS datas in /opt on the docker image
myapp_volume_mount = V1VolumeMount(mount_path='/opt', name='nfs-volume')

```

The 'mount_path' designates the directory of the volume that will be mounted in the Ubuntu container on Kubernetes Pod.

On /opt, on the pod deployed, you can access nfs data : 
![Airflow example on Air Liquide UC](/img/confiance_env/airflow_nfs.png)


### How to re-use this template 

1. Create a dockerfile in which you configure your environment (python version, lib) and you include your scripts.
Configure your script to read and write your data/results in a repo (Ex: /opt). You can re-use a repo of the docker base image or you can mkdir a dedicated repo.
2. Build, tag and push your docker image on Nexus (A gitlab-ci pipeline is available to do this automatically)
3. In the airflow-dag git repository : create a dag file for define the workflow :
  - Add NFS Volume configuration with path repo in 'mount_path' as defined for scripts in the docker image (Ex: /opt)
  - Define one task by script to execute : Each task is a KubernetesPodOperator() where filling the docker image name, volume configuration, command to execute one script on pod.
.


## Template Run One Job on Airflow

This template allows to execute a python script easily on airflow. 

- Step 1: Packing the docker image with the script to run.
- Step 2: Create the DAG file to run pipeline on airflow.

In this example the docker image is automatically built through a gitlab pipeline. You only have to push your code and put a tag on your branch to trigger the pipeline and update the artifact ( See [pipeline usage guide](/confiance_env/dev_practices/components_delivery/pipelines.md))
Then, as a reminder, to execute a DAG on airflow you have to push the python DAG code in a specific git repo (repo that synchronizes every minute with the airflow component : [Git repo link](https://git.irt-systemx.fr/confianceai/ec_1/infra/airflow-dags)) and then go to the UI to trigger the dag.
In this example, we are going to propose you a generic construction of DAG to push on git. It means that you only have to push your dag once on git because it will be generic to launch 1 task, and then you only use the airflow UI to launch a job by providing all the parameters that will populate the dag file.

### Docker image example

Structure repo :
- .gitlab-ci.yml : File that allows to use the generic pipeline to build and push a docker image on nexus.
- Dockerfile : Package your code on a docker image
- main.py : Code to run on airflow
- requirement.txt : Specifies the versions of the libraries 

Template example file : 

**.gitlab-ci.yml**
```
variables:
  PROJECT_NAME: "template-run-one-job" # Name of the Nexus repository where the image will be pushed
  PROJECT_VERSION: "$CI_COMMIT_TAG" # Tag of the image

include:
  - project: 'confianceai/ec_1/fa2_infrastructure/gitlab-ci-pipelines'
    ref: master
    file: 'docker-build-nexus.gitlab-ci.yml'

```

**Dockerfile**
```
FROM python:3.10.5-slim

ARG USER_NEXUS
ARG PASSWORD_NEXUS

WORKDIR /app

COPY main.py ./
COPY requirements.txt ./

RUN pip install -i https://$USER_NEXUS:$PASSWORD_NEXUS@repo.irtsysx.fr/repository/pypi-public/simple  -r requirements.txt

CMD [ "python", "./main.py"]
```
:::info
Note that you can specify the command to be executed in the Dockerfile or in the airflow DAG, depending on if you need to modify this command to launch multiple runs. In this case it's better not to put it here and to specify it in the DAG, it avoids rebuilding a whole docker image just to modify the command to execute.
If you put the command in the airflow DAG, replace the last line with ```CMD tail -f /dev/null```, it's to keep the container running until airflow run the command specify in dag.
:::

**main.py** : Your code to run

**requirement.txt** : Your requirements file for your code

[Repo git for this example - master branch](https://git.irt-systemx.fr/confianceai/ec_1/fa2_dockers/docker-run-one-job) 

In this same repo, you can find a more complex example based on **Thales UC** (execution of a python main with several dependent files, execution with GPU (this implies another from in Dockerfile)), on the [**demo_thales_amelie** branch](https://git.irt-systemx.fr/confianceai/ec_1/fa2_dockers/docker-run-one-job/-/tree/demo_thales_amelie).


### Generic example DAG  

You need to create you own dag file the first time and push it to git (airflow-dags repo).

To make this dag generic, we will use only variables in the dag, like this : ``` {{ dag_run.conf['KEY_VAR] }} ```

Then for running the dag, on the UI, you must select **Trigger DAG w/config** :
![Trigger DAG conf airflow](/img/confiance_env/trigger-conf-airflow.PNG)

This will give you the possibility to enter a json with the key/value to populate the DAG file. 


DAG file for simple example : 
```
from kubernetes.client import models as k8s
from airflow import DAG
from airflow.kubernetes.secret import Secret
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    'owner': 'USER.NAME',
    'depend_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
    'start_date': days_ago(1)
}

# No scheduling define in this example
with DAG(
    dag_id='template-run-one-job',
    default_args=default_args,
    schedule_interval=None,
    tags=['job','template'],
) as dag:
    step_run_job = KubernetesPodOperator(
        namespace='confiance',
        # Docker image to pull
        image="repo.irtsysx.fr:5086/{{ dag_run.conf['repo_name'] }}/{{ dag_run.conf['image_name'] }}:{{ dag_run.conf['image_tag'] }}",   
        image_pull_secrets=[k8s.V1LocalObjectReference('secretnexus')],   # Secret to pull Nexus
        image_pull_policy='Always',                                   
        # No command in this simple example, the command to run is in the Dockerfile
        #cmds=["bash", "-cx"],
        #arguments=["echo", "10"],
        # Pod name
        name="template-run-one-job",
        # Delete pod at the end of the task
        is_delete_operator_pod=True, ## Command to delete pod once cmds executed 
        in_cluster=True,
        task_id="run-job",
        get_logs=True,
    )
```

For trigger with configuration in airflow, use this json input :
```
{
  "repo_name": "docker-snapshots", 
  "image_name": "template-run-one-job", 
  "image_tag": "0.0.9-dev"
}
```


DAG file for Thales UC example :
```
from kubernetes.client import models as k8s
from airflow import DAG
from airflow.kubernetes.secret import Secret
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
from airflow.kubernetes.volume_mount import VolumeMount
from kubernetes.client import V1NFSVolumeSource, V1Volume, V1VolumeMount

### Mandatory section if you want to use NFS as mount point in your docker container :
# NFS configuration
nfs_volume = V1Volume(
    name='nfs-volume',
    nfs=V1NFSVolumeSource(path='/nfsdata', server='152.228.211.245'))
## You will have access to NFS datas in /nfsdata on the docker image
myapp_volume_mount = V1VolumeMount(mount_path='/nfsdata', name='nfs-volume')

### Mandatory section if you want to use GPU : 
affinityGPU={
    'nodeAffinity': {
        'requiredDuringSchedulingIgnoredDuringExecution': {
            'nodeSelectorTerms': [{
                'matchExpressions': [{
                    'key': 'node.kubernetes.io/instance-type',
                    'operator': 'In',
                    'values': [
                        't2-180'
                    ]
                }]
            }]
        }
    }
}

env_vars = {"CONFIANCE_BDD": "/nfsdata/EC1/UC_Thales_Aerial_Photograph_Interpretation/Dataset/XVIEW_Confiance"}

default_args = {
    'owner': 'USER.NAME',
    'depend_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
    'start_date': days_ago(1)
}

# No scheduling define in this example
with DAG(
    dag_id='template-thales-run-one-job',
    default_args=default_args,
    schedule_interval=None,
    tags=['job','template'],
) as dag:
    step_run_job = KubernetesPodOperator(
        namespace='confiance',
        # Docker image to pull
        image="repo.irtsysx.fr:5086/{{ dag_run.conf['repo_name'] }}/{{ dag_run.conf['image_name'] }}:{{ dag_run.conf['image_tag'] }}",      
        image_pull_secrets=[k8s.V1LocalObjectReference('secretnexus')],   # Secret to pull Nexus
        image_pull_policy='Always',
        # Volume to use
        volumes=[nfs_volume],
        volume_mounts=[myapp_volume_mount],
        # Command and args to run in pod 
        cmds=["bash", "-cx"],
        arguments=["{{ dag_run.conf['command'] }}"],
        # Pod name
        name="template-thales-run-one-job",
        # Delete pod at the end of the task
        is_delete_operator_pod=True, ## Command to delete pod once cmds executed 
        in_cluster=True,
        task_id="run-job",
        get_logs=True,
        affinity=affinityGPU,
        env_vars = env_vars
    )

```


For trigger with configuration in airflow, use this json input :
```
{
  "repo_name": "docker-snapshots", 
  "image_name": "demo-thales-run-one-job", 
  "image_tag": "0.0.1-dev",
  "command": "CUDA_VISIBLE_DEVICES=2 python3 train.py --opt config/opt/opt_XVIEW_CROP512_VEHICLES_train_S_Hyp0.yaml --workers 4"
  
}
```
By using airflow in this way, no more need to push in git each changes on the dag file to restart a pipeline, just restart the same dag with different parameters in the json input, to launch different commands or change the image tag.



