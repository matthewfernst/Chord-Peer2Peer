class InPlacementReq:
    def __init__(self, peer_to_check, requesting_port):
        self.peer_to_check = peer_to_check
        self.requesting_port = requesting_port

    def __repr__(self):
        return f'Peer Placement in Question:\n{self.peer_to_check}\n'

    def get_peer_to_check(self):
        return self.peer_to_check

    def get_requesting_port(self):
        return self.requesting_port
