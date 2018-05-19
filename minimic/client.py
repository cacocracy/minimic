import logging

from pyquery import PyQuery as pq
import requests

from misc import DEFAULT_USER_AGENT
from exceptions import MinimicException, LoginError


class ClientSession(object):
    def __init__(self, login_url: str, username: str,
                 password: str, verbose: bool = False) -> None:
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': DEFAULT_USER_AGENT
        })
        self.login_url = login_url
        self.username = username
        self.password = password
        self.pinfo = verbose

    def login(self) -> None:
        login_page = self.session.get(self.login_url)
        for x in pq(login_page.text)("input"):
            if x.name == 'authenticity_token':
                auth_token = x.value
                break
        else:
            raise LoginError('No authenticity_token found.')

        self.login_data = {
            'user[email]': self.username,
            'user[password]': self.password,
            'authenticity_token': auth_token
        }

        logging.info(f"About to POST login username={self.username}")
        response = self.session.post(self.login_url, data=self.login_data,
                                     headers=dict(Referer=self.login_url))

        if response.status_code != 200:
            raise LoginError(f'Did not receive 200 HTTP code: '
                              'Got {response.status_code}')
        else:
            if 'Sign out' not in response.text:
                raise LoginError('Did not appear to login -- '
                                 '"Sign out" token not found')
            time.sleep(2)
            logging.info(f"Logged in successfully as {self.username}")

    def logout(self) -> None:
        logging.warning('Method logout has no effect')

    def vprint(self, *args, **kwargs) -> None:
        if self.pinfo is True:
            print(*args, **kwargs)

