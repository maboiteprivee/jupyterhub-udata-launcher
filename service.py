from functools import wraps
import json
import os
from urllib.parse import quote

import requests
from flask import Flask, redirect, request
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell

from jupyterhub.services.auth import HubAuth

API_BASE = 'https://data.gouv.fr/api/1'
# TODO infer from context
NB_BASE = 'http://localhost:8000'
# NB_BASE = 'https://datanotebook.maboiteprivee.fr'
HOME_PATH = '/Users'
# HOME_PATH = '/home'

prefix = os.environ.get('JUPYTERHUB_SERVICE_PREFIX', '/')
auth = HubAuth(
    api_token=os.environ['JUPYTERHUB_API_TOKEN'],
    cache_max_age=60,
)

app = Flask(__name__)
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG') == 'True'


def authenticated(f):
    """Decorator for authenticating with the Hub"""
    @wraps(f)
    def decorated(*args, **kwargs):
        cookie = request.cookies.get(auth.cookie_name)
        token = request.headers.get(auth.auth_header_name)
        if cookie:
            user = auth.user_for_cookie(cookie)
        elif token:
            user = auth.user_for_token(token)
        else:
            user = None
        if user:
            return f(user, *args, **kwargs)
        else:
            # redirect to login url on failed auth
            return redirect(NB_BASE + auth.login_url + '?next=%s' % quote(request.path))
    return decorated


def get_resource(dataset_id, resource_id):
    r = requests.get('{}/datasets/{}'.format(API_BASE, dataset_id))
    if r.status_code != 200:
        raise Exception('Dataset %s not reachable' % dataset_id)
    dataset = r.json()
    resource = None
    for _resource in dataset['resources']:
        if _resource['id'] == resource_id:
            resource = _resource
    if not resource:
        raise Exception('Resource %s not found' % resource_id)
    return resource


def get_nb_md(**kwargs):
    return '''## Bienvenue sur `datanotebook` !

La ressource qui vous intéresse a été chargée ci-dessous dans un dataframe Pandas.

Enjoy!'''.format(kwargs)  # noqa


def get_nb_code(**kwargs):
    return '''import pandas as pd
df = pd.read_csv('{url}', sep=None, engine='python')
df.head()'''.format(**kwargs)


def go_to_nb(username, nb_name):
    nb_url = '{}/user/{}/notebooks/{}'.format(NB_BASE, username, nb_name)
    return redirect(nb_url)


def create_notebook(username, dataset_id, resource_id):
    nb_name = '{}.ipynb'.format(resource_id)
    nb_path = '{}/{}/{}'.format(HOME_PATH, username, nb_name)

    if os.path.isfile(nb_path):
        return go_to_nb(username, nb_name)

    resource = get_resource(dataset_id, resource_id)

    if not resource['format'].lower() == 'csv':
        raise Exception('Unsupported resource format %s' % resource['format'])

    url = resource['url']
    nb = new_notebook()
    nb.cells.append(new_markdown_cell(get_nb_md()))
    nb.cells.append(new_code_cell(get_nb_code(url=url)))

    with open(nb_path, 'w') as f:
        f.write(json.dumps(nb))

    return go_to_nb(username, nb_name)


@app.route('%s<dataset_id>/<resource_id>' % prefix)
@authenticated
def launchnotebook(user, dataset_id, resource_id):
    return create_notebook(user['name'], dataset_id, resource_id)
