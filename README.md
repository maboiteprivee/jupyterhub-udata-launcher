# jupyterhub-udata-launcher

:warning: Alpha stage.

This service is based on [JupyterHub](https://jupyterhub.readthedocs.io/en/latest/)
and lets you spawn a Jupyter notebook for a given [uData](https://github.com/opendatateam/udata)
resource.

At the moment, only CSV resources are supported. They're loaded into
a Pandas dataframe for convenience.

Users are logged in to the JupyterHub instance via GitHub Oauth. A home directory
is then created for them and theirs notebooks stored there.

## Install

Cf [JupyterHub install instructions](https://jupyterhub.readthedocs.io/en/latest/quickstart.html)

```
python3 -m venv pyenv && . pyenv/bin/activate
pip3 install -r requirements.txt
npm install -g configurable-http-proxy
```

Create a file named `jupyterhub_config_secret.py` and customize the GitHub settings:

```
c.GitHubOAuthenticator.oauth_callback_url = 'http://localhost:8000/hub/oauth_callback'
c.GitHubOAuthenticator.client_id = 'xxx'
c.GitHubOAuthenticator.client_secret = 'xxx'
c.Authenticator.admin_users = {'xxx'}
```

## Profit

```
jupyterhub
```

Redirect users to `http://<server>/services/launcher/<dataset>/<resource>` with
`<dataset>` and `<resource>` being the ids of the dataset and resource you want
to play with.
