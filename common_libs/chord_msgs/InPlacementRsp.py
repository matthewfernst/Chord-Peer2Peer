class InPlacementRsp:
    def __init__(self, successor, predecessor):
        self.successor = successor
        self.predecessor = predecessor

    def __repr__(self):
        return f'Successor {self.successor} and Predecessor {self.predecessor} found.'

    def get_successor(self):
        return self.successor

    def get_predecessor(self):
        return self.predecessor


