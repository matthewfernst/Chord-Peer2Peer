class FileWriteRspSuccess:
    def __init__(self, storing_peer, key, filename):
        self.storing_peer = storing_peer
        self.key = key
        self.filename = filename

    def __repr__(self):
        return f'WRITE SUCCESS for File {self.filename} as Key {self.key} on Storing Peer {self.storing_peer.get_peer_id()}\n'

    def get_storing_peer(self):
        return self.storing_peer

    def get_key(self):
        return self.key

    def get_filename(self):
        return self.filename
