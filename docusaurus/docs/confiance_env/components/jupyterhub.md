---
title: Jupyterhub
---

Jupyterhub is a Jupyter server with four main components:

- a Hub (tornado process) that is the heart of JupyterHub
- a configurable http proxy (node-http-proxy) that receives the requests from the client’s browser
- multiple single-user Jupyter notebook servers (Python/IPython/tornado) that are monitored by Spawners
- an authentication class that manages how users can access the system

Jupyter Link : https://jupyterhub.apps.confianceai-public.irtsysx.fr

## New features 16/11 :

### Multi images

In order to manage GPU resources, we have deployed images running on cpu too. You can now select your desired image from the following:
  1. GPU datascience environment: python 3.9 containing every libs for datascience (pytorch, tf, etc) with gpu compatibility 
  2. CPU datascience environment: same but only cpu.
  3. CPU Basic environment: contains standard libs for jupyter notebook but no datascience libs.

### Proxy

You can now use proxies in order to launch web apps on jupyterhub. Theses apps are only reachable through your jupyterhub instance (you can not share them) but they are handy to run live demos, test apps and so forth.

To do so, run your app on localhost as you would normally do on your local environment. Let's use flask as an example:
```
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
  return "<p>Hello, Jupyter world !</p>"
app.run(host='0.0.0.0', port=5000)
```
You can check the server is up with the following command on jupyterlab: `curl localhost:5000`

To access the jupyterlab hosted webapp from your **local browser** , you have to use your jupyterlab path:
https://jupyterhub.apps.confianceai-public.irtsysx.fr/user/name.surname/lab/... 

You must change the end of the path as follows: **.../name.surname/lab/...** becomes **.../name.surname/proxy/port/** which would be in our case:

https://jupyterhub.apps.confianceai-public.irtsysx.fr/user/name.surname/proxy/5000/

(don't forget the trailing slash)

You should now see your jupyterlab hosted webapp on your local browser.

:::remember
This works with any sort of python web-app, you simply need to make sure your app is exposed as localhost on a specific port so that you can proxy it correctly. For instance, using streamlit, use
st.set_option('browser.serverAddress', 'localhost') or modify ~/.streamlit/config.toml [streamlit doc](https://docs.streamlit.io/library/advanced-features/configuration)
:::

## Jupyter Remote Connection

### API Token

Before connecting Jupyterhub to your prefered IDE, please request an API token from the Confiance Jupyterhub instance:

- Connect to your account on Jupyterhub and go to the Hub Control Panel

![Hub Control Panel link](/img/confiance_env/jupyterhub_control_panel.png)

- Go to Token, and generate a new one by clicking on "Request new API token".

![Hub Control Panel Token](/img/confiance_env/jupyterhub_token.png)

:::caution
Be careful, keep the token in your prefered password manager as you will not be able to retrieve it once the tab is closed.
:::

### Visual Studio Code

Link to the [official documentation](https://code.visualstudio.com/datascience/jupyter-notebooks#_connect-to-a-remote-jupyter-server).

This paragraph presents the steps to connect a VS Code instance running in a local system (e.g., a user’s laptop) to JupyterHub Confiance server. Then, the local notebooks will be executable on remote Jupyter nodes in the Confiance platform (including GPU nodes).

- Install the Jupyter plugin in VS Code (identifier: `ms-toolsai.jupyter`) (:bulb: activate the precommercial version of the plugin)

- Open the VS Code command palette by pressing the keyboard shortcut:

  - On Window and Linuxs: `Ctrl+Shift+P` or `F1`.
  - On MacOS: `⇧⌘P` or `F1`.

- Search for Specify local or remote Jupyter server for connections

![VS Code Jupyter remote connection](/img/confiance_env/jupyterhub_remote.png)

- When prompted, select "Existing: Specify the URI of an existing server".
- Enter the following URL in the prompt, replace your username and your token and press Enter: `https://jupyterhub.apps.confianceai-public.irtsysx.fr/user/<your-username>/?token=<token>`
- Reload the VS Code window in order for the changes to be taken into account by pressing `Ctrl+R` or by opening the VS Code command palette and by choosing "Developer: Reload Window"
- When opening a new or an existing Notebook, you must now see the following statement about Jupyter remote connection at the bottom-right corner of VS Code and you will be able to choose a remote kernel to execute your code.

![VS Code Jupter remote information](/img/confiance_env/jupyterhub_remote_vscode.png)

### JetBrains PyCharm/DataSpell

Link to the [official documentation](https://www.jetbrains.com/help/pycharm/configuring-jupyter-notebook.html).

This paragraph presents the steps to connect a PyCharm/DataSpell instance running in a local system (e.g., a user’s laptop) to JupyterHub Confiance server. Then, the local notebooks will be executable on remote Jupyter nodes in the Confiance platform (including GPU nodes).

- Open a Jupyter notebook on your JetBrains IDE and click on `Configure Jupyter Server...` as shown below, a menu will open.

![Configure Jupyter Server... menu](/img/confiance_env/jupyterhub_pycharm_config.png)

- Set a new Configured Server with the URL of the Confiance Jupyterhub instance and click on the OK button.

![Jupyter Servers menu](/img/confiance_env/jupyterhub_pycharm_config_servers.png)

- Execute your notebook: a popup will open and ask for your username (usually `name.surname`), and for your previously requested API token.

![Jupyter Servers authentication](/img/confiance_env/jupyterhub_pycharm_auth.png)

- If everyone worked fine, you should see the following output when executing `!pwd`:

![Jupyter Servers authentication](/img/confiance_env/jupyterhub_pycharm_success.png)


## Configure access to Nexus

You need to create a configuration file so that you can install libs from the Nexus. You will then have access to the libraries developed by the different projects of the program. 

Create a file **pip.conf** here **/home/jovyan/.config/pip/pip.conf**, with the following contents :

```
[global]
index = https://repo.irtsysx.fr/repository/pypi-releases
index-url = https://repo.irtsysx.fr/repository/pypi-public/simple
no-cache-dir = false
```

Your IRT SystemX credentials will be required when you run _pip install_ command.
