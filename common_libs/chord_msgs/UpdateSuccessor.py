class UpdateSuccessor:
    def __init__(self, new_successor):
        self.new_successor = new_successor

    def __repr__(self):
        return f'New Successor:\n{self.new_successor}.'

    def get_new_successor(self):
        return self.new_successor

