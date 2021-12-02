

class NodeExitReq:
    def __init__(self, hash_id, host_port, nickname=None):
        self.node_id = hash_id
        self.host_port = host_port
        self.nickname = nickname

    def __repr__(self):
        return f'ID::{self.node_id} {self.host_port}'

    def get_node_id(self):
        return self.node_id

    def get_host_port(self):
        return self.host_port

    def get_nickname(self):
        return self.nickname