import requests
from datetime import datetime
from hashlib import sha1

from django.conf import settings


def generate_code(seed):
    code_key = u"%s-%s-%s" \
        % (settings.SECRET_KEY, datetime.now().isoformat(), seed)
    code = sha1(code_key).hexdigest()
    return code


def create_player(seed=""):
    URL = "http://beta.drglearning.com/api/v1/player/"
    code = generate_code(seed)
    params = {
        "callback": "callback",
        "format": "json",
        "code": code,
    }
    headers = {'content-type': 'application/json'}
    response = requests.get(URL, params=params, headers=headers)
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            return response
    return None


def get_player(code):
    URL = "http://beta.drglearning.com/api/v1/player/"
    params = {
        "callback": "callback",
        "format": "json",
        "code": code,
    }
    headers = {'content-type': 'application/json'}
    response = requests.get(URL, params=params, headers=headers)
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            return response
    return None


def update_player(code, token, display_name="", email="", options=None):
    URL = "http://beta.drglearning.com/api/v1/player/"
    params = {
        "callback": "callback",
        "code": code,
        "token": token,
        "display_name": display_name,
        "email": email,
        "format": "json",
    }
    if options:
        params.update({"options": options})
    headers = {'content-type': 'application/json'}
    response = requests.get(URL, params=params, headers=headers)
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            return response
    return None
