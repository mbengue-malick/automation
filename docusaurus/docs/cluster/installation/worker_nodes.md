---
sidebar_position: 5
title: Worker Nodes
---

:::warning
Before adding the worker nodes to the cluster, **you must install Weave** as detailed [here](./weave.md). Once this is done, you can come back to this steps to add them.
:::

## Add worker nodes

As seen [at the end of the cluster init](./nodes.md#initializing-the-master-nodes), this command will give you 2 commands as output:

```bash
# Do not execute it, this is only a reminder from the previous steps
sudo kubeadm init --pod-network-cidr=192.168.0.0/16 --cri-socket /run/containerd/containerd.sock --upload-certs --control-plane-endpoint=api.<cluster-name>.<domain-name>:6443
```

Configure the config file to run the kubectl commands:

```bash
mkdir -p $HOME/.kube
sudo cp -f /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

You can then add your worker node(s) to the cluster with **the second** `kubectl join` command that was provided above.

## (Optional) Add GPU nodes

:bulb: Before installing worker nodes with GPU, you must install NVIDIA Device Plugin on your Kubernetes Cluster with this command:

```bash
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.11.0/nvidia-device-plugin.yml
```

On the worker nodes that use GPUs, additional actions must be performed. First, you have to use the NGC NVIDIA OS image. It should be an Ubuntu in 20.04 with the NVIDIA driver ready to use.

After that, you must use the above commands to prepare this node as Kubernetes Server.

Then, you must change the location of the containerd folder as follows:

```bash
sudo file -s /dev/nvme0n1 # should return data if empty drive
sudo mkfs -t xfs /dev/nvme0n1
sudo mkdir /containerd
sudo xfs_admin -l /dev/nvme0n1
sudo xfs_admin -L containerd /dev/nvme0n1
```

And then edit `/etc/fstab` to add the following line at the bottom of the file:

```fstab
LABEL=containerd /containerd xfs defaults 0 0
```

Finally, you have to modify the containerd config file to have this :

```bash
sudo vi /etc/containerd/config.toml
```

<details>
<summary><code>/etc/containerd/config.toml</code></summary>

```toml
disabled_plugins = []
imports = []
oom_score = 0
plugin_dir = ""
required_plugins = []
root = "/containerd"
state = "/run/containerd"
version = 2

[cgroup]
 path = ""

[debug]
 address = ""
 format = ""
 gid = 0
 level = ""
 uid = 0

[grpc]
 address = "/run/containerd/containerd.sock"
 gid = 0
 max_recv_message_size = 16777216
 max_send_message_size = 16777216
 tcp_address = ""
 tcp_tls_cert = ""
 tcp_tls_key = ""
 uid = 0

[metrics]
 address = ""
 grpc_histogram = false

[plugins]
 [plugins."io.containerd.gc.v1.scheduler"]
   deletion_threshold = 0
   mutation_threshold = 100
   pause_threshold = 0.02
   schedule_delay = "0s"
   startup_delay = "100ms"

 [plugins."io.containerd.grpc.v1.cri"]
   disable_apparmor = false
   disable_cgroup = false
   disable_hugetlb_controller = true
   disable_proc_mount = false
   disable_tcp_service = true
   enable_selinux = false
   enable_tls_streaming = false
   ignore_image_defined_volumes = false
   max_concurrent_downloads = 3
   max_container_log_line_size = 16384
   netns_mounts_under_state_dir = false
   restrict_oom_score_adj = false
   sandbox_image = "k8s.gcr.io/pause:3.5"
   selinux_category_range = 1024
   stats_collect_period = 10
   stream_idle_timeout = "4h0m0s"
   stream_server_address = "127.0.0.1"
   stream_server_port = "0"
   systemd_cgroup = false
   tolerate_missing_hugetlb_controller = true
   unset_seccomp_profile = ""

   [plugins."io.containerd.grpc.v1.cri".cni]
     bin_dir = "/opt/cni/bin"
     conf_dir = "/etc/cni/net.d"
     conf_template = ""
     max_conf_num = 1

   [plugins."io.containerd.grpc.v1.cri".containerd]
     default_runtime_name = "runc"
     disable_snapshot_annotations = true
     discard_unpacked_layers = false
     no_pivot = false
     snapshotter = "overlayfs"

     [plugins."io.containerd.grpc.v1.cri".containerd.default_runtime]
       base_runtime_spec = ""
       container_annotations = []
       pod_annotations = []
       privileged_without_host_devices = false
       runtime_engine = ""
       runtime_root = ""
       runtime_type = ""
       [plugins."io.containerd.grpc.v1.cri".containerd.default_runtime.options]

     [plugins."io.containerd.grpc.v1.cri".containerd.runtimes]
       [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
         base_runtime_spec = ""
         container_annotations = []
         pod_annotations = []
         privileged_without_host_devices = false
         runtime_engine = ""
         runtime_root = ""
         runtime_type = "io.containerd.runtime.v1.linux"

         [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
           BinaryName = ""
           CriuImagePath = ""
           CriuPath = ""
           CriuWorkPath = ""
           IoGid = 0
           IoUid = 0
           NoNewKeyring = false
           NoPivotRoot = false
           Root = ""
           ShimCgroup = ""
           SystemdCgroup = false

     [plugins."io.containerd.grpc.v1.cri".containerd.untrusted_workload_runtime]
       base_runtime_spec = ""
       container_annotations = []
       pod_annotations = []
       privileged_without_host_devices = false
       runtime_engine = ""
       runtime_root = ""
       runtime_type = ""
       [plugins."io.containerd.grpc.v1.cri".containerd.untrusted_workload_runtime.options]

   [plugins."io.containerd.grpc.v1.cri".image_decryption]
     key_model = "node"

   [plugins."io.containerd.grpc.v1.cri".registry]
     config_path = ""
     [plugins."io.containerd.grpc.v1.cri".registry.auths]
     [plugins."io.containerd.grpc.v1.cri".registry.configs]
     [plugins."io.containerd.grpc.v1.cri".registry.headers]
     [plugins."io.containerd.grpc.v1.cri".registry.mirrors]

   [plugins."io.containerd.grpc.v1.cri".x509_key_pair_streaming]
     tls_cert_file = ""
     tls_key_file = ""

 [plugins."io.containerd.internal.v1.opt"]
   path = "/opt/containerd"

 [plugins."io.containerd.internal.v1.restart"]
   interval = "10s"

 [plugins."io.containerd.metadata.v1.bolt"]
   content_sharing_policy = "shared"

 [plugins."io.containerd.monitor.v1.cgroups"]
   no_prometheus = false

 [plugins."io.containerd.runtime.v1.linux"]
   no_shim = false
   runtime = "nvidia-container-runtime"
   runtime_root = ""
   shim = "containerd-shim"
   shim_debug = false

 [plugins."io.containerd.runtime.v2.task"]
   platforms = ["linux/amd64"]

 [plugins."io.containerd.service.v1.diff-service"]
   default = ["walking"]

 [plugins."io.containerd.snapshotter.v1.aufs"]
   root_path = ""

 [plugins."io.containerd.snapshotter.v1.btrfs"]
   root_path = ""

 [plugins."io.containerd.snapshotter.v1.devmapper"]
   async_remove = false
   base_image_size = ""
   pool_name = ""
   root_path = ""

 [plugins."io.containerd.snapshotter.v1.native"]
   root_path = ""

 [plugins."io.containerd.snapshotter.v1.overlayfs"]
   root_path = ""

 [plugins."io.containerd.snapshotter.v1.zfs"]
   root_path = ""

[proxy_plugins]
[stream_processors]
 [stream_processors."io.containerd.ocicrypt.decoder.v1.tar"]
   accepts = ["application/vnd.oci.image.layer.v1.tar+encrypted"]
   args = ["--decryption-keys-path", "/etc/containerd/ocicrypt/keys"]
   env = ["OCICRYPT_KEYPROVIDER_CONFIG=/etc/containerd/ocicrypt/ocicrypt_keyprovider.conf"]
   path = "ctd-decoder"
   returns = "application/vnd.oci.image.layer.v1.tar"

 [stream_processors."io.containerd.ocicrypt.decoder.v1.tar.gzip"]
   accepts = ["application/vnd.oci.image.layer.v1.tar+gzip+encrypted"]
   args = ["--decryption-keys-path", "/etc/containerd/ocicrypt/keys"]
   env = ["OCICRYPT_KEYPROVIDER_CONFIG=/etc/containerd/ocicrypt/ocicrypt_keyprovider.conf"]
   path = "ctd-decoder"
   returns = "application/vnd.oci.image.layer.v1.tar+gzip"

[timeouts]
 "io.containerd.timeout.shim.cleanup" = "5s"
 "io.containerd.timeout.shim.load" = "5s"
 "io.containerd.timeout.shim.shutdown" = "3s"
 "io.containerd.timeout.task.state" = "2s"


[ttrpc]
 address = ""
 gid = 0
 uid = 0
```

</details>

Your worker node is now ready to integrate the Kubernetes Cluster as a normal worker.

## NFS Configuration

On each worker and master you need to install the following package : ```sudo apt-get install nfs-common```

