import importlib

class Curation:
    """
    type: list/function
    """
    def __init__(self, type, result):
        self.type = type
        self.data = result
        self.result = self.data if type == 'list' else self.get()
    
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

