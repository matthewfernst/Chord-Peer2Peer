class MoveKeysRsp:

    def __init__(self, keys, storing_peer, requesting_peer):
        self.keys = keys
        self.storing_peer = storing_peer
        self.requesting_peer = requesting_peer

    def __repr__(self):
        return f'Keys {str([key for key in self.keys])[1:-1]} SUCCESSFULLY transfered from Peer {self.storing_peer.get_peer_id()} to Peer {self.requesting_peer.get_peer_id()}\n'

    def get_keys(self):
        return self.keys

    def get_storing_peer(self):
        return self.storing_peer

    def get_requesting_peer(self):
        return self.requesting_peer
