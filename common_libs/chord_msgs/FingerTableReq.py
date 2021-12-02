class FingerTableReq:
    def __init__(self, peer_to_check, id_to_check, requesting_port):
        self.peer_to_check = peer_to_check
        self.id_to_check = id_to_check
        self.requesting_port = requesting_port

    def __repr__(self):
        return f'Finger Table Request from {self.peer_to_check.get_host()}::{self.peer_to_check.get_peer_id()} Requesting Port {self.requesting_port}\n'

    def get_peer(self):
        return self.peer_to_check

    def get_id_to_check(self):
        return self.id_to_check

    def get_requesting_port(self):
        return self.requesting_port
