
class NodeExceptions(list):
    def __init__(self):
        super().__init__()

    def add_exception(self, exception):
        self.append(exception)