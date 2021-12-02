class FileReadReq:
    def __init__(self, requesting_peer, key, filename):
        self.requesting_peer = requesting_peer
        self.key = key
        self.filename = filename
        self.addr_hops = [requesting_peer]

    def __repr__(self):
        return f'READ REQUEST for File {self.filename} as Key {self.key} from Peer {self.requesting_peer.get_peer_id()}.\n'

    def get_requesting_peer(self):
        return self.requesting_peer

    def get_key(self):
        return self.key

    def get_filename(self):
        return self.filename

    def add_addr_hop(self, peer_address):
        self.addr_hops.append(peer_address)

    def get_addr_hops(self):
        return self.addr_hops
