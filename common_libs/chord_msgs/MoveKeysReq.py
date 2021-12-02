class MoveKeysReq:
    def __init__(self, requesting_peer, requesting_peer_successor):
        self.requesting_peer = requesting_peer
        self.requesting_peer_successor = requesting_peer_successor

    def __repr__(self):
        return f'Peer {self.requesting_peer.get_peer_id()} requesting Keys moved from Peer {self.requesting_peer_successor.get_peer_id()}.'

    def get_requesting_peer(self):
        return self.requesting_peer

    def get_requesting_peer_successor(self):
        return self.requesting_peer_successor