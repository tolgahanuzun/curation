import importlib
import logging

from lightsteem.client import Client
from lightsteem.datastructures import Operation

import settings

utopian_link = 'https://steemit.com/utopian-io/'
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class Curation:
    """
    type: list/function
    """
    def __init__(self, type, result):
        self.type = type
        self.data = result
        self.result = self.data if settings.type == 'list' else self.get()
    
    def get(self):
        """
        Default call funciton : run()
        Example; return app.run()
        """
        try:
            _funciton = importlib.import_module(self.data)
            return _funciton.run()
        except:
            return []


class Steemit:
    def __init__(self, username, steem_key):
        self.username = username
        self.client = Client(keys=[steem_key]) 
    
    def get_account(self):
        return self.client.account(self.username)

    def get_vp(self):
        account = self.get_account()
        return account.vp()

    def get_rc(self):
        account = self.get_account()
        return account.rc()

    def post_vote(self, voting_user, voting_link, weight=10000):
        try:
            op = Operation('vote', {
                "voter": self.username,
                "author": voting_user,
                "permlink": voting_link.split(f'{voting_user}/')[1],
                "weight": weight,
            })
            result = self.client.broadcast(op)
            logging.info(result)
        except:
            logging.info('Broadcast Fail!')
            return False
        return True


def avaible_link(link):
    """
    - Those who do not have a Utopian link are excluded.
    - Comment links are excluded.
    """

    if len(link.split(utopian_link)) <= 1:
        return False

    if '#' in link:
        return False
    return True