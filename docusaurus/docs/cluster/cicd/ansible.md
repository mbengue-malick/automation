---
sidebar_position: 3
title: Ansible
---

Ansible is used for the deployment automation process of components in the cluster. It is executed by the Gitlab runner as described [here](./gitlab_runner.md#ansible-executor)

## Structure

The [Ansible playbooks project](https://git.irt-systemx.fr/confianceai/ec_1/fa2_infrastructure/ansible-playbooks/) is structured as recommended in the official documentation. It uses playbooks, inventories per environment and group/hosts vars:

```bash
.
├── files # Files, vaulted or plain text, directly used by Ansible modules
├── gitlab-ci # Gitlab CICD Runner-related files
├── group_vars # Variables, vaulted or plain text, commonly used on all environments
│   └── all
│       ├── vars.yml
│       └── vault.yml
├── inventories # Definition of the environments
│   ├── preprod
│   │   ├── host_vars # Variables, vaulted or plain text, used only on the defined environment
│   │   │   └── localhost
│   │   │       ├── vars.yml
│   │   │       └── vault.yml
│   │   └── hosts # Hosts file, definition of the environment
│   ├── prod
│   │   ├── host_vars # Variables, vaulted or plain text, used only on the defined environment
│   │   │   └── localhost
│   │   │       ├── vars.yml
│   │   │       └── vault.yml
│   │   └── hosts # Hosts file, definition of the environment
├── templates # Template files, used with template module
│   ├── mlflow-minio-keys.yaml.j2
│   └── realm-export.json.j2
├── README.md
├── ansible.cfg
├── install_components.yml # Playbook
├── install_keycloak.yml # Playbook
├── install_webapp.yml # Playbook
├── requirements.yml # Required Ansible-Galaxy collections to install before executing a playbook
└── template_values.yml # Playbook
```

:::info
In the present inventories, the `hosts` file only points towards `localhost` as the Gitlab runner, which is inside the cluster, executes commands directly inside this same cluster.
:::

## Pipeline

The Gitlab CICD pipeline can be launched automatically, triggered by other pipelines ("real" CICD), or manually if needed. It has several parameters, all described in the `ansible-playbooks` repository. Here is an example of such parameterized pipeline, to deploy Pixano in the production namespace:

![Gitlab CICD pipeline parameters](/img/cluster/cicd_ansible_pipeline.png)

To trigger the pipeline from an other one, use the stage below. It uses the Gitlab API, and the project ID (see highlighted line), that you can find by searching over the [projects list API](https://git.irt-systemx.fr/api/v4/projects).

```yaml
trigger:
  stage: trigger_cd
  script:
    - apk update && apk add curl
    - 'curl -s
      -X POST
      -F token=${CI_JOB_TOKEN}
      -F ref=master
      -F "variables[TRIGGERER_PIPELINE_ID]=${CI_PIPELINE_ID}"
      -F "variables[CLUSTER_ENVIRONMENT]=prod"
      -F "variables[OTHER_VAR]=true"
      -F "variables[ANOTHER_VAR]='a string'"
      # highlight-next-line
      https://git.irt-systemx.fr/api/v4/projects/3726/trigger/pipeline'
  only:
    - tags
    - master
```

## Dev workflow

:::info
To develop new playbooks, add or modify inventories, etc... please follow the [Git Flow](/confiance_env/dev_practices/git_flow.md).
:::

### Local Ansible install

Ansible can be installed in WSL2 on your Windows machine (if you have a Debian-based machine, you can still follow this tutorial). It can be useful to interact with vault files, to use `ansible-lint` or to be able to use the VS Code Ansible plugin (extension ID: `vscoss.vscode-ansible`). In WSL2, launch the below commands.

```bash
sudo apt install -y ansible
ansible --version
```

To use the plugin in VS Code, open your project from your WSL2 instance: `code /my/repository/directory`.

### Work with inventories and variables

In Ansible, variables can be defined in multiple places, following a precedence principle which is described in the [official documentation](https://docs.ansible.com/ansible/2.5/user_guide/playbooks_variables.html#variable-precedence-where-should-i-put-a-variable). We chose to use `group_vars` to store commonly used variables on all environments and `host_vars` per environment to store variables only used on the defined environment. In each directory, a `vars.yml` and a `vault.yml` files are defined: the first is in plain text, and the second is encrypted using `ansible-vault`.

### Work with vault files

Vault files can be any kind of files but they are encrypted by Ansible using AES-256. In the repository, vault files share the same password, which can be found in [Passbolt](https://passbolt.irt-systemx.fr). Those files are used to store sensitive variables, such as passwords or tokens, and Kubernetes secrets. To unvault (decrypt) or vault a file, you can use the following commands:

```bash
ansible-vault decrypt ./my/vaulted/file.extension
ansible-vault encrypt ./my/vaulted/file.extension
```

In the Gitlab CI pipeline, the password to decrypt the vaults is stored as a masked variable in the CI/CD repository's settings but it is also possible to set it as a parameter when launching a pipeline.

### Work with template files (Jinja)

Template files can be any kind of files but they can be templated, i.e. have some of its values changed by Ansible. The templating language used is Jinja, the official specifications can be read [here](https://jinja.palletsprojects.com/en/3.1.x/templates/). To be read by Ansible, template files **must** end with `.j2` and follow the Jinja syntax.

Here is an example of a YAML templated file, and the Ansible module call to template it:

```jinja title="values.yaml.j2"
ingress:
  enabled: {{ has_ingress }}
  hostname: {{ ingress_url }}
```

```yaml title="playbook.yml"
- name: Template values file
  template:
    src: "./values.yaml.j2"
    dest: "./values.yaml"
  vars:
    has_ingress: true
    ingress_url: my.ingress.com
```
