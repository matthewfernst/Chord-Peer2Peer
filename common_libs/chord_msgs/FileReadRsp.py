class FileReadRsp:
    def __init__(self, storing_peer, key, filename, binary_data, addr_hops=list()):
        self.storing_peer = storing_peer
        self.key = key
        self.filename = filename
        self.binary_data = binary_data
        self.addr_hops = addr_hops

    def __repr__(self):
        return f'READ SUCCESS on File {self.filename} as Key {self.key} from Storing Peer {self.storing_peer.get_peer_id()}.\n'

    def get_storing_peer(self):
        return self.storing_peer

    def get_key(self):
        return self.key

    def get_filename(self):
        return self.filename

    def get_binary_data(self):
        return self.binary_data

    def get_addr_hops(self):
        return self.addr_hops

