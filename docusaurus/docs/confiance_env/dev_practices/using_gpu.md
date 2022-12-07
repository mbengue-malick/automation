---
sidebar_position: 3
title: GPU guide
---

#### This is a guide for using gpu in Confiance environment, it's split in two parts: 
1. How to properly use gpus on the environment
2. How to deploy gpu-enabled images in an airflow pipeline.

## 1.  How to properlu use gpus on the environment

Example of issues: Many users face the **"CUDA_ERROR_OUT_OF_MEMORY: out of memory"** issue.

The gpu guide is located in the following repository: [https://git.irt-systemx.fr/confianceai/ec_1/infra/tutorials](https://git.irt-systemx.fr/confianceai/ec_1/infra/tutorials), it contains 3 notebook that tackle the following subjects:
- Select a gpu device in Pytorch / Tensorflow.
- Optimize VRAM (gpu ram) use in Pytorch / Tensorflow
- GPU Parallelism (distributed training in tensorflow)

## 2. How to deploy GPU-enabled images in an airflow pipeline
   
If you want to train on gpus, your dockerfile must start with pulling a gpu-enabled image, but what images are available? This guide is made to do a smooth transition from your working jupyterhub environment to a working packaged image to be tested on airflow.

### 1. First step: test your dependencies on jupyterhub (ie requirements and compatibility)
Currently, we provide a gpu-enabled pod for every user on jupyter with cuda 11.2, you can use a virtualenv to use whatever python library youn need.

### 2. Second step: If your code can run on jupyter, then you can package it in a dockerfile
   The choice for your image is according to the level of controle you want: 
   - **pre-packaged images** is the simpler option:

      - Tensorflow versions **2.4 / 2.5 / 2.6** --> FROM  tensorflow/tensorflow:latest-gpu OR nvcr.io/nvidia/tensorflow:22.07-tf2-py3

        TF Compatibility: https://www.tensorflow.org/install/source#gpu

        | Version  | Python  | Compilateur  | compil tool  | cuDNN  | CUDA |
        |---|---|---|---|---|---|
        |tensorflow-2.6.0|3.6-3.9|GCC 7.3.1|Bazel 3.7.2|8.1	|11.2|
        |tensorflow-2.5.0|3.6-3.9|GCC 7.3.1|Bazel 3.7.2|8.1	|11.2|
        |tensorflow-2.4.0|3.6-3.8|GCC 7.3.1|Bazel 3.7.0|8.0|11.0 |



      - Pytorch :**1.12** 1.12.0-cuda11.3-cudnn8-runtime 2.76 GB https://hub.docker.com/r/pytorch/pytorch/tags OR  nvcr.io/nvidia/pytorch:22.06-py3 6.53 GB 

        Pytorch Compatibility: TORCH 1.12.1
        https://pytorch.org/get-started/locally/ : 

        11.6: pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116
        11.3: ok

    Then you can install whatever library you need from your requirements (don't forget versions)

    Example of such dockerfile installing pytorch on a pre built tensorflow image.

    ```bash
    FROM nvcr.io/nvidia/tensorflow:22.04-tf2-py3
    ENV TZ=Europe/Paris
    RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
    RUN pip install --no-cache-dir --user torch --extra-index-url https://download.pytorch.org/whl/cu113
    COPY ./src /src
    CMD ['python3', '/src/is_cuda_available.py']
    ```


   - **CUDA IMAGES**:  if you want more control on versions and libs, use cuda images but you might face some issues: (works with pytorch but issues with tensorflow)
Comes in 3 types according to nvidia doc (https://catalog.ngc.nvidia.com/orgs/nvidia/containers/cuda):

    - base: Includes the CUDA runtime (cudart): we are not using this one
    - runtime: Builds on the base and includes the CUDA math libraries, and NCCL. A runtime image that also includes cuDNN is available.
    - devel: Builds on the runtime and includes headers, development tools for building CUDA images. These images are particularly useful for multi-stage builds.

example: NCCL for // GPU requires runtime (or devel)

**from runtime**: 

FROM nvidia/cuda:11.7.0-runtime-ubuntu20.04 




<!-- add picture here![Integration process](/img/confiance_env/git_workflow.png) -->

