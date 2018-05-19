import os
import time
from unittest import TestCase

import minimic


# Ensure the following fields exist
URL = os.environ['MINIMIC_URL']
USERNAME = os.environ['MINIMIC_USERNAME']
PASSWORD = os.environ['MINIMIC_PASSWORD']


def pause(f):
    def pauser(*args, **kwargs):
        time.sleep(0.5)
        try:
            f(*args, **kwargs)
        except:
            time.sleep(0.5)
            raise
    return pauser


class TestClient(TestCase):
    def test_create_client(self):
        c = minimic.SessionClient(URL, USERNAME, PASSWORD)

    @pause
    def test_login_wrong_credentials(self):
        c = minimic.SessionClient(URL, USERNAME, PASSWORD)
        with self.assertRaises(minimic.LoginError):
            c.login()

    @pause
    def test_login_credentials(self):
        c = minimic.SessionClient(URL, USERNAME, PASSWORD)
        c.login()

