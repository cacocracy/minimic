from unittest import TestCase
import shutil
import time
import os

import requests

import minimic


# Ensure the following fields exist
URL = os.environ['MINIMIC_URL']
SIGNIN = os.environ['MINIMIC_SIGNIN']
USERNAME = os.environ['MINIMIC_USERNAME']
PASSWORD = os.environ['MINIMIC_PASSWORD']


# Cannot run tests if remote is unreachable
r = requests.get(SIGNIN, timeout=5)
if r.status_code != 200:
    print(f"Unreachable remote: {SIGNIN} ({r.status_code})")


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
#    def test_create_client(self):
#        c = minimic.ClientSession(SIGNIN, USERNAME, PASSWORD)
#
#    @pause
#    def test_login_credentials(self):
#        c = minimic.ClientSession(SIGNIN, USERNAME, PASSWORD)
#        c.login()
#        c.logout()
#
#    @pause
#    def test_login_wrong_credentials(self):
#        c = minimic.ClientSession(SIGNIN, 'nonexist@email', 'wrongpass22')
#        with self.assertRaises(minimic.LoginError):
#            c.login()
#        c.logout()

    @pause
    def test_save_album(self):
        c = minimic.ClientSession(SIGNIN, USERNAME, PASSWORD)
        c.login()
        target_dir = '/tmp/minimic-unittest'
        os.makedirs(target_dir, exist_ok=True)
        try:
            r = minimic.save_album(c, f"{URL}/galleries/95318",
                                   target_dir)
            # Test response metadata
            self.assertEqual(r.get('images'), 11)
            self.assertEqual(r.get('profile_id'), 341084)
            self.assertEqual(r.get('album_id'), 95318)
            self.assertEqual(r.get('locked_images_count'), 4)
            self.assertTrue(r.get('likes_count') > 1000)
            self.assertIn('!!!', r.get('description'))
            self.assertIn('new', r.get('album_name').lower())

            # Test images download properly
            inames = [i for i in os.listdir(os.path.join(target_dir, 'p341084-a95318'))
                      if '.json' not in i]
            self.assertEqual(len(inames), 11)
        finally:
            shutil.rmtree(target_dir)
            c.logout()

