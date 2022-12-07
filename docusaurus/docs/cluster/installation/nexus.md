---
title: Nexus
sidebar_position: 9
---

Installation of a Nexus repository to store Docker images and Python libraries. Based on Sonatype Nexus Repository running on Podman in a Ubuntu 20.04 VM.

Sources:

- [Sonatype doc](https://blog.sonatype.com/sonatype-nexus-installation-using-docker)
- [LinuxTricks - Debian](https://www.linuxtricks.fr/wiki/print.php?id=722)

## Server FQDN

The server needs to have a defined FQDN. Set it if needed and register it on the DNS (not shown here):

```bash
$ hostnamectl set-hostname repo.irtsysx.fr
$ hostnamectl status
   Static hostname: repo.irtsysx.fr
         Icon name: computer-vm
           Chassis: vm
        Machine ID: xxxxxxxxxxxxxxxxxxxx
           Boot ID: xxxxxxxxxxxxxxxxxxxx
    Virtualization: kvm
  Operating System: Ubuntu 20.04.4 LTS
            Kernel: Linux 5.4.0-104-generic
      Architecture: x86-64
$ sudo shutdown -r now
```

:::info

<details>
<summary>Improvement clue</summary>
Firewall configuration:

```bash
sudo ufw allow proto tcp from any to any port 22,80,443,5085
sudo ufw status
```

</details>
:::

## OS automatic update

To befenit from automatic update of the base OS (Ubuntu-20.04 in our case), it is recommended to apply the below files modifications.

```diff title="/etc/apt/apt.conf.d/20auto-upgrades"
APT::Periodic::Update-Package-Lists "1"; # apt update
APT::Periodic::Unattended-Upgrade "1"; # Download updates
+ APT::Periodic::Download-Upgradeable-Packages "1"; # Install updates
+ APT::Periodic::AutocleanInterval "7"; # Weekly sudo apt autoclean -y
```

Clean old kernels automatically:

```diff title="etc/apt/apt.conf.d/50unattended-upgrades
...
+ Unattended-Upgrade::Remove-Unused-Kernel-Packages "true"; # l.83
...
+ Unattended-Upgrade::Automatic-Reboot "true"; # l.94
...
+ Unattended-Upgrade::Automatic-Reboot-Time "02:00"; # l.103
```

Verify the configuration has been taken into account:

```bash
unattended-upgrades --debug --dry-run
```

Verfiy the upgrades are logging to the kernel:

```bash
$ ls -la /var/log/unattended-upgrades
total 36
drwxr-x--- 2 root adm     4096 May  2 01:51 .
drwxr-xr-x 8 root syslog  4096 May  9 09:34 ..
-rw-r--r-- 1 root adm     6769 May  6 06:56 unattended-upgrades-dpkg.log
-rw-r--r-- 1 root root     113 May  9 09:33 unattended-upgrades-shutdown.log
-rw-r--r-- 1 root root   13683 May  9 12:55 unattended-upgrades.log
```

Here is a script to execute to have everything auto-updateded:

```bash
$ cat << EOF > ~/bin/maj.sh
#!/bin/bash

echo "=== Maj OS ==="
sudo apt autoclean -y && sudo apt update -y && sudo apt upgrade -y && sudo apt autoremove --purge -y

echo "=== Inventory Ansible ==="
grep -v '^\s*$\|^\s*\#' /etc/ansible/hosts

echo "=== Maj Pip3 ==="
pip3 list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip3 install -U

echo "=== OS need to restart ? ==="
if [ -f /var/run/reboot-required ]; then
  echo 'reboot required'
else
  echo 'no reboot need'
fi
EOF
$ chmod +x ~/bin/maj.sh
$ ~/bin/maj.sh
```

## Let's Encrypt

### Install

Once the FQDN is registered on the DNS, we can configure Let's Encrypt. Binary install:

```bash
sudo apt-get update
sudo apt-get install certbot
```

### Configure

```bash
$ export DOMAIN="repo.irtsysx.fr"
$ export ALERTS_EMAIL="surname.name@irt-systemx.fr"
$ sudo systemctl stop nginx
$ sudo certbot certonly --standalone -d $DOMAIN --preferred-challenges http --agree-tos -n -m $ALERTS_EMAIL --keep-until-expiring
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Plugins selected: Authenticator standalone, Installer None
Obtaining a new certificate
Performing the following challenges:
http-01 challenge for repo.irtsysx.fr
Waiting for verification...
Cleaning up challenges

IMPORTANT NOTES:
 - Congratulations! Your certificate and chain have been saved at:
   /etc/letsencrypt/live/repo.irtsysx.fr/fullchain.pem
   Your key file has been saved at:
   /etc/letsencrypt/live/repo.irtsysx.fr/privkey.pem
   Your cert will expire on 2022-06-16. To obtain a new or tweaked
   version of this certificate in the future, simply run certbot
   again. To non-interactively renew *all* of your certificates, run
   "certbot renew"
 - Your account credentials have been saved in your Certbot
   configuration directory at /etc/letsencrypt. You should make a
   secure backup of this folder now. This configuration directory will
   also contain certificates and private keys obtained by Certbot so
   making regular backups of this folder is ideal.
 - If you like Certbot, please consider supporting our work by:

   Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
   Donating to EFF:                    https://eff.org/donate-le
```

Verify that four files have been created:

```bash
$ sudo ls -al /etc/letsencrypt/live/repo.irtsysx.fr
total 12
drwxr-xr-x 2 root root 4096 Apr  1 09:39 .
drwx------ 4 root root 4096 Apr  1 09:39 ..
-rw-r--r-- 1 root root  692 Apr  1 09:39 README
lrwxrwxrwx 1 root root   39 Apr  1 09:39 cert.pem -> ../../archive/repo.irtsysx.fr/cert1.pem
lrwxrwxrwx 1 root root   40 Apr  1 09:39 chain.pem -> ../../archive/repo.irtsysx.fr/chain1.pem
lrwxrwxrwx 1 root root   44 Apr  1 09:39 fullchain.pem -> ../../archive/repo.irtsysx.fr/fullchain1.pem
lrwxrwxrwx 1 root root   42 Apr  1 09:39 privkey.pem -> ../../archive/repo.irtsysx.fr/privkey1.pem
```

It is also recommended to verify that Let's Encrypt has enabled automatic renewal: Let's Encrypt certificates are only valid for **3 month**. Certbot offers two services to manage it:

```bash
$ sudo systemctl status certbot.timer
● certbot.timer - Run certbot twice daily
     Loaded: loaded (/lib/systemd/system/certbot.timer; enabled; vendor preset: enabled)
     Active: active (waiting) since Fri 2022-03-18 10:25:13 UTC; 25min ago
    Trigger: Fri 2022-03-18 12:00:43 UTC; 1h 9min left
   Triggers: ● certbot.service

Mar 18 10:25:13 repo.irtsysx.fr systemd[1]: Started Run certbot twice daily.
$ sudo systemctl status certbot.service
● certbot.service - Certbot
     Loaded: loaded (/lib/systemd/system/certbot.service; static; vendor preset: enabled)
     Active: inactive (dead)
TriggeredBy: ● certbot.timer
       Docs: file:///usr/share/doc/python-certbot-doc/html/index.html
             https://letsencrypt.readthedocs.io/en/latest/
```

Two files need to be created to extend and re-power certbot. Indeed it needs port 80 to work. And it is cerbot that does the automatic renewal of certificates.

~~~bash
sudo bash -c 'cat <<EOF > /etc/letsencrypt/renewal-hooks/pre/nginx_stop.sh
#!/bin/bash
echo "LetEncrypts stopping nginx"
sudo systemctl stop nginx.service
EOF'
sudo chmod 744 /etc/letsencrypt/renewal-hooks/pre/nginx_stop.sh

sudo bash -c 'cat <<EOF > /etc/letsencrypt/renewal-hooks/post/nginx_start.sh
#!/bin/bash
echo "LetEncrypts starting nginx"
sudo systemctl start nginx.service
EOF'
sudo chmod 744 /etc/letsencrypt/renewal-hooks/post/nginx_start.sh
~~~

### Verify installation

It is important to test the proper functioning of the certificates. The ports `80` and `443` must be opened and listening for this test.

```bash
$ sudo systemctl stop nginx.service
$ sudo certbot renew --dry-run
Saving debug log to /var/log/letsencrypt/letsencrypt.log

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Processing /etc/letsencrypt/renewal/repo.irtsysx.fr.conf
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Cert not due for renewal, but simulating renewal for dry run
Plugins selected: Authenticator standalone, Installer None
Renewing an existing certificate
Performing the following challenges:
http-01 challenge for repo.irtsysx.fr
Waiting for verification...
Cleaning up challenges

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
new certificate deployed without reload, fullchain is
/etc/letsencrypt/live/repo.irtsysx.fr/fullchain.pem
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
** DRY RUN: simulating 'certbot renew' close to cert expiry
**          (The test certificates below have not been saved.)

Congratulations, all renewals succeeded. The following certs have been renewed:
  /etc/letsencrypt/live/repo.irtsysx.fr/fullchain.pem (success)
** DRY RUN: simulating 'certbot renew' close to cert expiry
**          (The test certificates above have not been saved.)
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
$ sudo systemctl start nginx.service
```

### Notes

Even if it is not very common, here is how to delete a certificate. It can be useful if the FQDN has changed.

```bash
$ sudo certbot delete --cert-name repo.irtsysx.fr
Saving debug log to /var/log/letsencrypt/letsencrypt.log

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Deleted all files relating to certificate repo.irtsysx.fr.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
```

## NGINX

### Install and configure

As we will install Nexus as a container, we will use a reverse-proxy through NGINX.

```bash
$ sudo apt -y install nginx
$ sudo systemctl start nginx
systemctl enable nginx
$ sudo systemctl enable nginx
Synchronizing state of nginx.service with SysV service script with /lib/systemd/systemd-sysv-install.
Executing: /lib/systemd/systemd-sysv-install enable nginx
```

Here is a NGINX configuration for Nexus, taking into account the special ports Docker needs to store images.

```conf title="/etc/nginx/conf.d/nexus.conf"
proxy_send_timeout 120;
proxy_read_timeout 300;
proxy_buffering off;

server {
  listen 80;
  server_name repo.irtsysx.fr;
  server_tokens off;
  return 301 https://$host$request_uri;
}

server {
  listen *:443;
  server_name repo.irtsysx.fr;

  server_tokens off;
  access_log /var/log/nginx/repo.irtsysx.fr-access.log;
  error_log /var/log/nginx/repo.irtsysx.fr-error.log;
  ssl_certificate /etc/letsencrypt/live/repo.irtsysx.fr/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/repo.irtsysx.fr/privkey.pem;

  # allow large uploads of files
  client_max_body_size 1G;
  ssl on;

  # optimize downloading files larger than 1G
  #proxy_max_temp_file_size 2G;

  location / {
      # Use IPv4 upstream address instead of DNS name to avoid attempts by nginx to use IPv6 DNS lookup
      proxy_pass http://127.0.0.1:8081/;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-Host $host:$server_port;
      proxy_set_header X-Forwarded-Server $host;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto "https";
  }
}

server {
  listen *:5085;
  server_name repo.irtsysx.fr;

  server_tokens off;
  access_log /var/log/nginx/repo.irtsysx.fr-access.log;
  error_log /var/log/nginx/repo.irtsysx.fr-error.log;
  ssl_certificate /etc/letsencrypt/live/repo.irtsysx.fr/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/repo.irtsysx.fr/privkey.pem;

  # allow large uploads of files
  client_max_body_size 1G;
  ssl on;

  # optimize downloading files larger than 1G
  #proxy_max_temp_file_size 2G;

  location / {
      # Use IPv4 upstream address instead of DNS name to avoid attempts by nginx to use IPv6 DNS lookup
      proxy_pass http://127.0.0.1:8085/;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-Host $host:$server_port;
      proxy_set_header X-Forwarded-Server $host;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto "https";
  }
}
```

### Verify installation

We need to verify that NGINX has taken into account its new configuration.

```bash
$ sudo nginx -t
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

Then we restart NGINX and we test the HTTPS connection. It is important not to have TLS errors.

```bash
$ sudo systemctl restart nginx
$ sudo systemctl enable nginx
Synchronizing state of nginx.service with SysV service script with /lib/systemd/systemd-sysv-install.
Executing: /lib/systemd/systemd-sysv-install enable nginx
$ curl https://repo.irtsysx.fr
<html>
<head><title>302 Found</title></head>
<body>
<center><h1>302 Found</h1></center>
<hr><center>nginx/1.18.0 (Ubuntu)</center>
</body>
</html>
```

## Podman

```bash
# user root
sudo su -
apt-get update -y
apt-get install curl wget gnupg2 -y
source /etc/os-release
sh -c "echo 'deb http://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_${VERSION_ID}/ /' > /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list"
wget -nv https://download.opensuse.org/repositories/devel:kubic:libcontainers:stable/xUbuntu_${VERSION_ID}/Release.key -O- | apt-key add -
apt-get update -qq -y
apt-get -qq --yes install podman
podman --version
podman info
```

Verify the configuration:

```conf title="/etc/containers/registries.conf"
# ========================================
# ... end of file
[registries.insecure]
registries = [ ]
# If you need to block pull access from a registry, uncomment the section below
# and add the registries fully-qualified name.
# Docker only
[registries.block]
registries = [ ]
# ========================================
```

Test Podman and the connection with Docker Hub:

```bash
# standard user
nexus@repo:~$ podman run hello-world
Resolved "hello-world" as an alias (/etc/containers/registries.conf.d/000-shortnames.conf)
Trying to pull docker.io/library/hello-world:latest...
Getting image source signatures
Copying blob 2db29710123e done
Copying config feb5d9fea6 done
Writing manifest to image destination
Storing signatures

Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/
```

## Nexus user

First, create a user `nexus`, then verify its subids.

```bash
sudo adduser nexus # Be careful to store its password in somewhere safe
loginctl enable-linger nexus
```

```bash
$ grep nexus /etc/subuid /etc/subgid
/etc/subuid:nexus:296608:65536
/etc/subgid:nexus:296608:65536
```

:::caution
Be careful, the subid starts at 296608 but the chown sets it at 296607. It may be a bug inherent to Podman that generates files by doing subid-1 but nothing is sure.

```bash
sudo chown -R 296807:296807 ${NEXUS_BASE_DIR:-/data/nexus}
sudo chown nexus:296807 ${NEXUS_BASE_DIR:-/data/nexus}
sudo chmod 770 ${NEXUS_BASE_DIR:-/data/nexus}
```

:::

## Nexus deployment

Sources:

- [Sonatype](https://github.com/sonatype/docker-nexus3)
- [Nexus - Docker based](http://ratwaterblog.blogspot.com/2018/04/local-docker-based-nexus-repo.html)
- [Nexus for Docker images](https://blog.sonatype.com/using-nexus-3-as-your-repository-part-3-docker-images)

### Podman container

Launch the Podman container of Nexus:

```bash
# Study:  https://hub.docker.com/r/sonatype/nexus3/
# Modify this to suit your needs
NEXUS_BASE_DIR=/data/nexus

# If needed
podman rm nexus

# start nexus with host volume at NEXUS_BASE_DIR/nexus
podman run -d \
  --publish 8081:8081 \
  --publish 8085:8085 \
  --publish 8086:8086 \
  --env INSTALL4J_ADD_VM_PARAMS="-Xms2703m -Xmx2703m -XX:MaxDirectMemorySize=2703m -Djava.util.prefs.userRoot=/nexus-data/javaprefs" \
  -v ${NEXUS_BASE_DIR:-/data/nexus}:/nexus-data \
  --ulimit=nofile=4096:65536 \
  --name nexus \
  --restart always \
  sonatype/nexus3:3.38.1
```

The admin password is shown in the logs but can also be retrieved by looking at the following file (which disappears once the admin password is changed):

```bash
podman exec -it nexus /bin/bash -c 'cat /nexus-data/admin.password'
```

To stop Nexus, it is as simple as the following command:

```bash
podman stop nexus
```

:::caution
If Nexus has already been started and some OCI ulimit errors appear, the Nexus container must be removed:

```bash
podman rm nexus
podman run ....
```

:::

### Service

We use Podman and not Docker to run Nexus, so the container works in user mode. This same user has to launch the service.

```bash
# sudo sh -c 'podman generate systemd --new --name nexus > /etc/systemd/system/nexus.service'

# Source : https://answers.launchpad.net/ubuntu/+source/systemd/+question/287454
# Set in ~/.profile
export XDG_RUNTIME_DIR=/run/user/`id -u`
# Then activate
loginctl enable-linger nexus

# Personal service
mkdir -p $HOME/.config/systemd/user
podman generate systemd --new --name nexus > /home/nexus/.config/systemd/user/nexus.service
systemctl --user enable nexus.service

# With general systemd:
# sudo cp /home/nexus/.config/systemd/user/nexus.service /etc/systemd/system
# sudo systemctl daemon-reload
# sudo systemctl list-unit-files | grep nexus
# sudo systemctl enable --now nexus.service
# sudo systemctl status nexus
```

### Verify the service

Here, the service is owned by a user, which allows its isolation rootless.

```bash
nexus@repo:~$ systemctl --user start nexus.service
nexus@repo:~$ systemctl --user status nexus.service
● nexus.service - Podman container-nexus.service
     Loaded: loaded (/home/nexus/.config/systemd/user/nexus.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2022-04-07 07:29:04 UTC; 9s ago
       Docs: man:podman-generate-systemd(1)
    Process: 36403 ExecStartPre=/bin/rm -f /run/user/1003/nexus.service.ctr-id (code=exited, status=0/SUCCESS)
   Main PID: 36509 (conmon)
     CGroup: /user.slice/user-1003.slice/user@1003.service/nexus.service
             ├─36489 /usr/bin/fuse-overlayfs -o ,lowerdir=/home/nexus/.local/share/containers/storage/overlay/l/WE5H7TGM2RC6E2UMTWJ7DCFCCS:/home/nexus/.local/share>
             ├─36490 /usr/bin/slirp4netns --disable-host-loopback --mtu=65520 --enable-sandbox --enable-seccomp -c -e 3 -r 4 --netns-type=path /run/user/1003/netns>
             ├─36492 containers-rootlessport
             ├─36500 containers-rootlessport-child
             ├─36509 /usr/libexec/podman/conmon --api-version 1 -c 2c7fc8d2fd427fa393ce66b13bb4c41273ae875c9730b642bcadd422f54d3759 -u 2c7fc8d2fd427fa393ce66b13bb4>
             └─36512 /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.282.b08-2.el8_3.x86_64/jre/bin/java -server -Dinstall4j.jvmDir=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.282>

Apr 07 07:29:11 repo.irtsysx.fr nexus[36509]: 2022-04-07 07:29:11,015+0000 INFO  [FelixStartLevel] *SYSTEM org.sonatype.nexus.bootstrap.jetty.JettyServer - Applyin>
Apr 07 07:29:11 repo.irtsysx.fr nexus[36509]: 2022-04-07 07:29:11,037+0000 INFO  [jetty-main-1] *SYSTEM org.sonatype.nexus.bootstrap.jetty.JettyServer - Starting: >
Apr 07 07:29:11 repo.irtsysx.fr nexus[36509]: 2022-04-07 07:29:11,045+0000 INFO  [jetty-main-1] *SYSTEM org.eclipse.jetty.server.Server - jetty-9.4.43.v20210629; b>
Apr 07 07:29:11 repo.irtsysx.fr nexus[36509]: 2022-04-07 07:29:11,110+0000 INFO  [jetty-main-1] *SYSTEM org.eclipse.jetty.server.session - DefaultSessionIdManager >
Apr 07 07:29:11 repo.irtsysx.fr nexus[36509]: 2022-04-07 07:29:11,111+0000 INFO  [jetty-main-1] *SYSTEM org.eclipse.jetty.server.session - No SessionScavenger set,>
Apr 07 07:29:11 repo.irtsysx.fr nexus[36509]: 2022-04-07 07:29:11,112+0000 INFO  [jetty-main-1] *SYSTEM org.eclipse.jetty.server.session - node0 Scavenging every 6>
Apr 07 07:29:11 repo.irtsysx.fr nexus[36509]: 2022-04-07 07:29:11,121+0000 INFO  [jetty-main-1] *SYSTEM org.sonatype.nexus.bootstrap.osgi.BootstrapListener - Initi>
Apr 07 07:29:11 repo.irtsysx.fr nexus[36509]: 2022-04-07 07:29:11,128+0000 INFO  [jetty-main-1] *SYSTEM org.sonatype.nexus.bootstrap.osgi.BootstrapListener - Loadi>
Apr 07 07:29:11 repo.irtsysx.fr nexus[36509]: 2022-04-07 07:29:11,130+0000 INFO  [jetty-main-1] *SYSTEM org.sonatype.nexus.bootstrap.osgi.BootstrapListener - Insta>
Apr 07 07:29:13 repo.irtsysx.fr nexus[36509]: 2022-04-07 07:29:13,946+0000 INFO  [jetty-main-1] *SYSTEM org.ehcache.core.osgi.EhcacheActivator - Detected OSGi Envi>
```

## IAM

Verify that the Active Directory can be called:

```bash
ldapsearch -H ldaps://auth.irt-systemx.fr -x -W -D "surname.name@irt-systemx.local" -b "dc=irt-systemx,dc=local" "(sAMAccountName=svc.ai-ec1)" -o nettimeout=5 /var/lib/dpkg/lock-frontend
```

### Access configuration to the Active Directory

![Nexus LDAP configuration](/img/cluster/nexus/nexus-ldap-1.PNG)

Configure the access for Confiance.AI AD users:

- Object class: `person`
- User filter: `(&(objectClass=user)(memberOf=CN=Confiance_AI,OU=Groupes Globaux,OU=Groupes,OU=Nano-Innov,DC=irt-systemx,DC=local))`
- User ID attribute: `sAMAccountName`

![Nexus LDAP configuration](/img/cluster/nexus/nexus-ldap-2.PNG)

![Nexus LDAP configuration](/img/cluster/nexus/nexus-ldap-3.PNG)

Admin roles for the Docker repository

![Admin roles for the Docker repository](/img/cluster/nexus/nexus-roles-4.PNG)

Developer role for the Docker repository

![Developer role for the Docker repository](/img/cluster/nexus/nexus-roles-5.PNG)

Admin roles for the PyPi repository

![Admin roles for the PyPi repository](/img/cluster/nexus/nexus-roles-6.PNG)

Developer roles for the PyPi repository

![Developer roles for the PyPi repository](/img/cluster/nexus/nexus-roles-7.PNG)

:::info
_Pro tip_: there is no RBAC group management, so it is useful to create a default role for the connected users. First, create a "developer" role with all the above "developer" roles set

![Developer parent role](/img/cluster/nexus/nexus-default-role-9.PNG)

Then affect it to the default role

![Default role](/img/cluster/nexus/nexus-default-role-8.PNG)
:::

## Docker repository usage

```bash
podman login repo.irtsysx.fr:5086
podman build -t getting-started .
podman push getting-started
podman image push getting-started
podman --log-level debug push getting-started
podman tag docker.io/library/hello-world localhost:5000/hello-world

/mydocker$ podman images
REPOSITORY                 TAG         IMAGE ID      CREATED         SIZE
localhost/getting-started  latest      b7926c2704e5  17 minutes ago  321 MB
<none>                     <none>      2abbd3d0e39a  2 days ago      321 MB
docker.io/library/node     12-alpine   314ec282a089  2 days ago      95.5 MB
docker.io/sonatype/nexus   oss         741e09e185dd  2 weeks ago     476 MB
docker.io/sonatype/nexus   latest      741e09e185dd  2 weeks ago     476 MB
docker.io/sonatype/nexus3  3.38.0      1e1d45f195b1  4 weeks ago     676 MB

podman tag localhost/getting-started repo.irtsysx.fr:5085/getting-started
podman --log-level debug push repo.irtsysx.fr:5085/getting-started
```

```bash
/mydocker$ podman tag localhost/getting-started repo.irtsysx.fr:5086/getting-started
/mydocker$ podman login repo.irtsysx.fr:5086
Username: admin
Password:
Login Succeeded!
/mydocker$ podman --log-level debug push repo.irtsysx.fr:5086/getting-started
INFO[0000] podman filtering at log level debug
DEBU[0000] Called push.PersistentPreRunE(podman --log-level debug push repo.irtsysx.fr:5086/getting-started)
DEBU[0000] overlay storage already configured with a mount-program
DEBU[0000] Merged system config "/usr/share/containers/containers.conf"
DEBU[0000] Merged system config "/home/surname.name/.config/containers/containers.conf"
....
DEBU[0008] Upload of layer sha256:b7926c2704e506b10b48bcb1403ef400de4899d779b764b345314da37833ae48 complete
Writing manifest to image destination
DEBU[0008] PUT https://repo.irtsysx.fr:5086/v2/getting-started/manifests/latest
Storing signatures
DEBU[0009] Called push.PersistentPostRunE(podman --log-level debug push repo.irtsysx.fr:5086/getting-started)
```

## Troubleshooting

### Blocked Docker login

Error of type: `Remote error from secret service: org.freedesktop.DBus.Error.ServiceUnknown: The name org.freedesktop.secrets was not provided by any .service files`

```bash
sudo apt install gnupg2 pass
```

Then log in with Docker:

```bash
surname.name@calcul-01:~$ docker login -u surname.name repo.irtsysx.fr:5086
Password:
WARNING! Your password will be stored unencrypted in /home/surname.name/.docker/config.json.
Configure a credential helper to remove this warning. See
https://docs.docker.com/engine/reference/commandline/login/#credentials-store

Login Succeeded
```

### Blocked Docker image push

The initial confifuration was 2G. Set it to 8Go

```bash
ubuntu@repo:~$ sudo su - nexus
nexus@repo:~$ systemctl --user status nexus.service
● nexus.service - Podman container-nexus.service
     Loaded: loaded (/home/nexus/.config/systemd/user/nexus.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2022-06-10 02:00:19 UTC; 5 days ago
       Docs: man:podman-generate-systemd(1)
    Process: 882 ExecStartPre=/bin/rm -f /run/user/1003/nexus.service.ctr-id (code=exited, status=0/SUCCESS)
   Main PID: 1002 (conmon)
     CGroup: /user.slice/user-1003.slice/user@1003.service/nexus.service
             ├─ 973 /usr/bin/fuse-overlayfs -o ,lowerdir=/home/nexus/.local/share/containers/storage/overlay/l/WE5H7TGM2RC6E2UMTWJ7DCFCCS:/home/nexus/.local/share/containers/storage/overl>
             ├─ 974 /usr/bin/slirp4netns --disable-host-loopback --mtu=65520 --enable-sandbox --enable-seccomp -c -e 3 -r 4 --netns-type=path /run/user/1003/netns/cni-4908ba05-fe1e-ffe4-4>
             ├─ 981 containers-rootlessport
             ├─ 991 containers-rootlessport-child
             ├─1002 /usr/libexec/podman/conmon --api-version 1 -c b7709223b36b305409ba41b32436d64f8c4da6cb0536f8be3f1efaf36fa2bd3d -u b7709223b36b305409ba41b32436d64f8c4da6cb0536f8be3f1ef>
             └─1005 /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.282.b08-2.el8_3.x86_64/jre/bin/java -server -Dinstall4j.jvmDir=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.282.b08-2.el8_3.x86_64/jre ->

Jun 15 14:40:00 repo.irtsysx.fr nexus[1002]: 2022-06-15 14:40:00,007+0000 INFO  [quartz-9-thread-19] *SYSTEM org.sonatype.nexus.quartz.internal.task.QuartzTaskInfo - Task 'Storage facet c>
Jun 15 14:40:00 repo.irtsysx.fr nexus[1002]: 2022-06-15 14:40:00,013+0000 INFO  [quartz-9-thread-19] *SYSTEM org.sonatype.nexus.quartz.internal.task.QuartzTaskInfo - Task 'Storage facet c>
Jun 15 14:41:33 repo.irtsysx.fr nexus[1002]: 2022-06-15 14:41:33,986+0000 INFO  [qtp1948215953-2975] ingrid.fiquet org.sonatype.nexus.rapture.internal.security.SessionServlet - Deleting s>
Jun 15 14:45:24 repo.irtsysx.fr nexus[1002]: 2022-06-15 14:45:24,592+0000 INFO  [qtp1948215953-3047] admin org.sonatype.nexus.rapture.internal.security.SessionServlet - Created session fo>
Jun 15 14:50:00 repo.irtsysx.fr nexus[1002]: 2022-06-15 14:50:00,005+0000 INFO  [quartz-9-thread-19] *SYSTEM org.sonatype.nexus.quartz.internal.task.QuartzTaskInfo - Task 'Storage facet c>
Jun 15 14:50:00 repo.irtsysx.fr nexus[1002]: 2022-06-15 14:50:00,009+0000 INFO  [quartz-9-thread-19] *SYSTEM org.sonatype.nexus.quartz.internal.task.QuartzTaskInfo - Task 'Storage facet c>
Jun 15 15:00:00 repo.irtsysx.fr nexus[1002]: 2022-06-15 15:00:00,004+0000 INFO  [quartz-9-thread-19] *SYSTEM org.sonatype.nexus.quartz.internal.task.QuartzTaskInfo - Task 'Storage facet c>
Jun 15 15:00:00 repo.irtsysx.fr nexus[1002]: 2022-06-15 15:00:00,007+0000 INFO  [quartz-9-thread-19] *SYSTEM org.sonatype.nexus.quartz.internal.task.QuartzTaskInfo - Task 'Storage facet c>
Jun 15 15:10:00 repo.irtsysx.fr nexus[1002]: 2022-06-15 15:10:00,008+0000 INFO  [quartz-9-thread-19] *SYSTEM org.sonatype.nexus.quartz.internal.task.QuartzTaskInfo - Task 'Storage facet c>
Jun 15 15:10:00 repo.irtsysx.fr nexus[1002]: 2022-06-15 15:10:00,012+0000 INFO  [quartz-9-thread-19] *SYSTEM org.sonatype.nexus.quartz.internal.task.QuartzTaskInfo - Task 'Storage
nexus@repo:~$ systemctl --user stop nexus.service
nexus@repo:~$ vi /home/nexus/.config/systemd/user/nexus.service
nexus@repo:~$ # Delete ports xx87, xx88 et xx89 and upgrade to 3.39.0
nexus@repo:~$ systemctl --user daemon-reload
nexus@repo:~$ podman pull sonatype/nexus3:3.39.0
✔ docker.io/sonatype/nexus3:3.39.0
Trying to pull docker.io/sonatype/nexus3:3.39.0...
Getting image source signatures
Copying blob 545277d80005 done
Copying blob 6e6913462068 done
Copying blob 10b49635409a done
Copying blob f70d60810c69 done
Writing manifest to image destination
Storing signatures
aab1398bb647ffef8475d129e7012d5b6c8c8d0ce3d1225f956c021f65d30173
nexus@repo:~$ systemctl --user start nexus.service
nexus@repo:~$ systemctl --user status nexus.service
● nexus.service - Podman container-nexus.service
     Loaded: loaded (/home/nexus/.config/systemd/user/nexus.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2022-06-15 15:18:12 UTC; 34s ago
       Docs: man:podman-generate-systemd(1)
   Main PID: 63458 (conmon)
     CGroup: /user.slice/user-1003.slice/user@1003.service/nexus.service
             ├─63434 /usr/bin/slirp4netns --disable-host-loopback --mtu=65520 --enable-sandbox --enable-seccomp -c -e 3 -r 4 --netns-type=path /run/user/1003/netns/cni-09a59698-05bc-61e9->
             ├─63437 /usr/bin/fuse-overlayfs -o ,lowerdir=/home/nexus/.local/share/containers/storage/overlay/l/WE5H7TGM2RC6E2UMTWJ7DCFCCS:/home/nexus/.local/share/containers/storage/over>
             ├─63439 containers-rootlessport
             ├─63447 containers-rootlessport-child
             ├─63458 /usr/libexec/podman/conmon --api-version 1 -c 2dde61ed637834d7ff476be5d5ad665e6fbc67e539cdd7318b17efb6c5e15c1e -u 2dde61ed637834d7ff476be5d5ad665e6fbc67e539cdd7318b17>
             └─63461 /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.282.b08-2.el8_3.x86_64/jre/bin/java -server -Dinstall4j.jvmDir=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.282.b08-2.el8_3.x86_64/jre >

Jun 15 15:18:47 repo.irtsysx.fr nexus[63458]: 2022-06-15 15:18:47,168+0000 INFO  [FelixStartLevel] *SYSTEM org.sonatype.nexus.extender.NexusBundleTracker - ACTIVATED wrap_file_system_com_>
Jun 15 15:18:47 repo.irtsysx.fr nexus[63458]: 2022-06-15 15:18:47,169+0000 INFO  [FelixStartLevel] *SYSTEM org.sonatype.nexus.extender.NexusBundleTracker - ACTIVATING com.sonatype.nexus.l>
Jun 15 15:18:47 repo.irtsysx.fr nexus[63458]: 2022-06-15 15:18:47,205+0000 INFO  [FelixStartLevel] *SYSTEM org.sonatype.nexus.extender.NexusBundleTracker - ACTIVATED com.sonatype.nexus.li>
Jun 15 15:18:47 repo.irtsysx.fr nexus[63458]: 2022-06-15 15:18:47,206+0000 INFO  [FelixStartLevel] *SYSTEM org.sonatype.nexus.extender.NexusBundleTracker - ACTIVATING com.sonatype.nexus.p>
Jun 15 15:18:47 repo.irtsysx.fr nexus[63458]: 2022-06-15 15:18:47,274+0000 INFO  [FelixStartLevel] *SYSTEM org.sonatype.nexus.extender.NexusBundleTracker - ACTIVATED com.sonatype.nexus.pl>
Jun 15 15:18:47 repo.irtsysx.fr nexus[63458]: 2022-06-15 15:18:47,277+0000 INFO  [FelixStartLevel] *SYSTEM org.sonatype.nexus.extender.NexusBundleTracker - ACTIVATING com.sonatype.nexus.p>
Jun 15 15:18:47 repo.irtsysx.fr nexus[63458]: 2022-06-15 15:18:47,308+0000 INFO  [FelixStartLevel] *SYSTEM org.sonatype.nexus.extender.NexusBundleTracker - ACTIVATED com.sonatype.nexus.pl>
Jun 15 15:18:47 repo.irtsysx.fr nexus[63458]: 2022-06-15 15:18:47,413+0000 INFO  [FelixStartLevel] *SYSTEM org.sonatype.nexus.extender.NexusBundleTracker - ACTIVATING com.sonatype.nexus.p>
Jun 15 15:18:47 repo.irtsysx.fr nexus[63458]: 2022-06-15 15:18:47,573+0000 INFO  [FelixStartLevel] *SYSTEM org.sonatype.nexus.extender.NexusBundleTracker - ACTIVATED com.sonatype.nexus.pl>
Jun 15 15:18:47 repo.irtsysx.fr nexus[63458]: 2022-06-15 15:18:47,575+0000 INFO  [FelixStartLevel] *SYSTEM org.sonatype.nexus.extender.NexusBundleTracker - ACTIVATING com.sonatype.nexus.p

ubuntu@repo:~$ sudo systemctl stop nginx.service
ubuntu@repo:~$ sudo vi /etc/nginx/conf.d/nexus.conf
ubuntu@repo:~$ sudo nginx -t
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
ubuntu@repo:~$ systemctl --user daemon-reload
ubuntu@repo:~$ sudo systemctl start nginx.service
ubuntu@repo:~$ sudo systemctl status nginx.service
● nginx.service - A high performance web server and a reverse proxy server
     Loaded: loaded (/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2022-06-15 15:34:51 UTC; 5s ago
       Docs: man:nginx(8)
    Process: 64376 ExecStartPre=/usr/sbin/nginx -t -q -g daemon on; master_process on; (code=exited, status=0/SUCCESS)
    Process: 64390 ExecStart=/usr/sbin/nginx -g daemon on; master_process on; (code=exited, status=0/SUCCESS)
   Main PID: 64391 (nginx)
      Tasks: 5 (limit: 9278)
     Memory: 5.3M
     CGroup: /system.slice/nginx.service
             ├─64391 nginx: master process /usr/sbin/nginx -g daemon on; master_process on;
             ├─64392 nginx: worker process
             ├─64393 nginx: worker process
             ├─64394 nginx: worker process
             └─64395 nginx: worker process

Jun 15 15:34:51 repo.irtsysx.fr systemd[1]: Starting A high performance web server and a reverse proxy server...
Jun 15 15:34:51 repo.irtsysx.fr systemd[1]: Started A high performance web server and a reverse proxy server.
```

# Maintenance extension de disk

# Augmenter le disk avec OVH puis

~~~bash
sudo pvresize /dev/sdb1
sudo lvresize --resizefs --size +50G /dev/vg00/datavolume1
lsblk
~~~

Mettre les taches suivantes dans le Task de Nexus afin de faire de la libération toujours les jours, donc en daily :
- "Docker delete incomplete uploads" à 1h00
- "Docker - Delete unused manifests and images" à 2h00
- "Admin - Compact blob store" à 3h00
