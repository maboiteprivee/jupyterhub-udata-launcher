from oauthenticator.github import GitHubOAuthenticator

c = get_config()  # noqa

c.JupyterHub.authenticator_class = GitHubOAuthenticator

# override in jupyterhub_config_secret.py
c.GitHubOAuthenticator.oauth_callback_url = 'http://localhost:8000/hub/oauth_callback'
c.GitHubOAuthenticator.client_id = 'xxx'
c.GitHubOAuthenticator.client_secret = 'xxx'
c.Authenticator.admin_users = {'xxx'}

c.JupyterHub.services = [
    {
        'name': 'launcher',
        'url': 'http://127.0.0.1:10101',
        'command': ['flask', 'run', '--port=10101'],
        'environment': {
            'FLASK_APP': 'service.py',
            'FLASK_DEBUG': 'True',
        }
    },
]

load_subconfig('jupyterhub_config_secret.py')  # noqa
