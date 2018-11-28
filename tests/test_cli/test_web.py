import hashlib
import hmac
import json
import os
import pytest

from filabel.web import webhook_verify_signature
from filabel.web import process_webhook_ping
from filabel.web import create_app
from filabel.web import process_webhook_pr

from .conftest import CONFIGS_PATH

def test_webhook():

    encoding = 'utf-8'
    payload = "{payload: payload}".encode(encoding)
    secret = "secret"
    signature = 'sha1=' + hmac.new(secret.encode(encoding), payload, hashlib.sha1).hexdigest()

    assert webhook_verify_signature(payload, signature, secret, encoding=encoding)


def test_invalid_webhook():

    encoding = 'utf-8'
    payload = "{payload: payload}".encode(encoding)
    badSecret = "bad secret"

    bad_signature = hmac.new(badSecret.encode(encoding), payload, hashlib.sha1).hexdigest()

    assert not webhook_verify_signature(payload, bad_signature, badSecret, encoding=encoding)


def test_process_webhook_ping(github):

    os.environ["FILABEL_CONFIG"] = CONFIGS_PATH + "/labels.abc.cfg" + ':' + CONFIGS_PATH + '/auth.fff.cfg'

    test_app = create_app(github=github)

    payload = '{ "repository":{ "full_name":"name" }, "hook_id": "123" }'

    j = json.loads(payload)

    with test_app.app_context():
        res, code = process_webhook_ping(j)

    assert res == 'PONG'
    assert code == 200

