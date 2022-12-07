---
sidebar_position: 6
title: RookCeph
---

RookCeph is a Cloud-Native Storage for Kubernetes.

To configure RookCeph, several configurations are available: either connect to an existing Ceph cluster, or generate a Ceph cluster thanks to RookCeph directly on the worker nodes. Our installation will be based on the last option.

## Requirements

RookCeph requires at least 3 worker nodes.

:warning: Warning: RookCeph will consume a lot of resources, so you need to anticipate or dedicate **3 worker nodes** for this purpose. Then you need to attach volumes to these worker nodes. These volumes will be used as OSDs for our internal Ceph cluster. Since a Ceph cluster redunds its data 3 times, **the number of disks must always be at least 3**.

## Step 1

Retrieve RookCeph installation folder and proceed with the installation:

```bash
git clone --single-branch --branch master https://github.com/rook/rook.git cd rook/deploy/examples kubectl create -f crds.yaml -f common.yaml -f operator.yaml
```

## Step 2

Edit the cluster.yaml file by reducing the number of mgr to 1 (variable count) and run the following command:

```bash
kubectl create -f cluster.yaml
```

## Step 3

Check the installation using this kubectl command, this is what you should get:

```bash
$ kubectl -n rook-ceph get pod
NAME                                                 READY   STATUS      RESTARTS   AGE
csi-cephfsplugin-provisioner-d77bb49c6-n5tgs         5/5     Running     0          140s
csi-cephfsplugin-provisioner-d77bb49c6-v9rvn         5/5     Running     0          140s
csi-cephfsplugin-rthrp                               3/3     Running     0          140s
csi-rbdplugin-hbsm7                                  3/3     Running     0          140s
csi-rbdplugin-provisioner-5b5cd64fd-nvk6c            6/6     Running     0          140s
csi-rbdplugin-provisioner-5b5cd64fd-q7bxl            6/6     Running     0          140s
rook-ceph-crashcollector-minikube-5b57b7c5d4-hfldl   1/1     Running     0          105s
rook-ceph-mgr-a-64cd7cdf54-j8b5p                     1/1     Running     0          77s
rook-ceph-mon-a-694bb7987d-fp9w7                     1/1     Running     0          105s
rook-ceph-mon-b-856fdd5cb9-5h2qk                     1/1     Running     0          94s
rook-ceph-mon-c-57545897fc-j576h                     1/1     Running     0          85s
rook-ceph-operator-85f5b946bd-s8grz                  1/1     Running     0          92m
rook-ceph-osd-0-6bb747b6c5-lnvb6                     1/1     Running     0          23s
rook-ceph-osd-1-7f67f9646d-44p7v                     1/1     Running     0          24s
rook-ceph-osd-2-6cd4b776ff-v4d68                     1/1     Running     0          25s
rook-ceph-osd-prepare-node1-vx2rz                    0/2     Completed   0          60s
rook-ceph-osd-prepare-node2-ab3fd                    0/2     Completed   0          60s
rook-ceph-osd-prepare-node3-w4xyz                    0/2     Completed   0          60s
```

## Step 4

Generate the storageClass in order to use your new RookCeph cluster.

- [storageClass Block](https://rook.io/rook/latest/Storage-Configuration/Block-Storage-RBD/block-storage/)
- [storageClass FileSystem](https://rook.io/rook/latest/Storage-Configuration/Shared-Filesystem-CephFS/filesystem-storage/)
- [storageClass Object](https://rook.io/rook/latest/Storage-Configuration/Object-Storage-RGW/object-storage/)
