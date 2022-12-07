---
title: Keycloak
---

## Import Realm

Keycloak allows us to export and import parts or whole Realms by clicking on the **Import** and **Export** buttons on the administration console. It is advised to export the whole Realm, with clients and groups/roles to make a backup of your configuration.

:::caution
Be careful, the export does not work for the secrets: client secrets, passwords, tokens... You will have to replace them in the exported `.json` file manually if you want to keep them.

:thought_balloon: In Confiance CD playbook, the `.json` file is templated with Jinja2 syntax, and can be generated with the passwords that are kept in the Ansible Vault.
:::

You can find an example of configuration by downloading [this file](./realm-export.json). You can then import it in your Keycloak instance in order to see which configuration is applied to clients.

## Restrict access to clients

[Reference](https://stackoverflow.com/questions/54305880/how-can-i-restrict-client-access-to-only-one-group-of-users-in-keycloak)

Keycloak is able to control the access to one or many applications to one or several group of users, by configuring roles and scopes.

Let us consider the following case: I want to restrict the access to Jupyterhub to users having the role `Jupyter_User`.

### Role and scope creation

- Go to client roles (realm -> Clients -> `jupyterhub` -> Roles)
- Click on _Add Role_ -> enter Name (e.g. `jupyter_access`) -> click _Save_
- Go to Client Scopes (realm -> Client Scopes)
- Click on _Create_ -> enter Name (e.g. `jupyter-scope`) & leave Protocol `openid-connect` -> click _Save_
- Go to _Mappers_ section -> click _Add Builtin_ and select all the mappers needed by your client application
- Assign Client Role `jupyter_access` in _Scope_ tab by choosing client application `jupyterhub` in _Client Roles_ drop down
- Return to your client `jupyterhub` -> click _Client Scopes_ -> unassign all the scopes and assign `jupyter-scope` to the _Default Client Scopes_ section

### User management

Now, you will not be able to log into Jupyterhub anymore, as the role `jupyter_access` is not assigned to any user or group. Let us create a new group and assign the role and a user to it.

- Create Group: realm -> Groups -> Click _New_ -> enter Name `Jupyter_User` -> click _Save_
- In _Role Mappings_, choose `jupyterhub` in _Client Roles_ drop down, and assign the role `jupyter_access`
- Assign a `test-user` to `Jupyter_User` (realm -> Users -> Click on `test-user` -> Groups -> Select `Jupyter_User` -> Click _Join_)

:::info Option
It is also possible to create a global role `access` (for example) in realm -> Roles and configure it for multiple clients if we want to restrict their access for the same group of users.
:::

## Add OIDC client - Jupyterhub

[Tutorial](https://osc.github.io/ood-documentation/release-1.3/authentication/tutorial-oidc-keycloak-rhel7/configure-keycloak-webui.html#add-oidc-client-template)
