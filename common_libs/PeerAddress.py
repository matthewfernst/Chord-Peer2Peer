
class PeerAddress:

    def __init__(self, peer_id, host, port):
        self.peer_id = peer_id
        self.host = host
        self.port = port

    def __repr__(self):
        address = f"{'_' * 52}\n"
        address += f"|{' ':^16}|{' ':^16}|{' ':^16}|\n"
        address += f"|{'Peer ID':^16}|{'Host':^16}|{'Port':^16}|\n"
        address += f"|{'_' * 16}|{'_' * 16}|{'_' * 16}|\n"
        address += f"|{' ':^16}|{' ':^16}|{' ':^16}|\n"
        address += f"|{self.peer_id:^16}|{self.host:^16}|{self.port:^16}|\n"
        address += f"|{'_' * 16}|{'_' * 16}|{'_' * 16}|\n"
        return address

    def __eq__(self, other):
        if isinstance(other, PeerAddress):
            return self.peer_id == other.peer_id and self.host == other.host and self.port == other.port
        return False

    def get_peer_id(self):
        return self.peer_id

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def get_host_port(self):
        return f'{self.get_host()}:{self.get_port()}'