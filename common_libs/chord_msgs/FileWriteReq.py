class FileWriteReq:
    def __init__(self, requesting_peer, key, filename, requesting_port):
        self.requesting_peer = requesting_peer
        self.key = key
        self.filename = filename
        self.requesting_port = requesting_port
        self.addr_hops = list()

    def __repr__(self):
            return f'WRITE REQUEST for File {self.filename} as Key {self.key} from Peer {self.requesting_peer.get_peer_id()}.\n'

    def get_requesting_peer(self):
        return self.requesting_peer

    def get_key(self):
        return self.key

    def get_filename(self):
        return self.filename

    def get_requesting_port(self):
        return self.requesting_port

    def add_addr_hop(self, peer_addr):
        self.addr_hops.append(peer_addr)

    def get_addr_hops(self):
        return self.addr_hops
