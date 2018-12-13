import importlib

import settings

utopian_link = 'https://steemit.com/utopian-io/'


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
