class FileTransfer:
    def __init__(self, requesting_peer, key, filename, binary_data):
        self.requesting_peer = requesting_peer
        self.key = key
        self.filename = filename
        self.binary_data = binary_data

    def __repr__(self):
        return f"Key {self.key} transfer to Peer {self.requesting_peer.get_peer_id()}.\n"

    def get_requesting_peer(self):
        return self.requesting_peer

    def get_key(self):
        return self.key

    def get_filename(self):
        return self.filename

    def get_binary_data(self):
        return self.binary_data
