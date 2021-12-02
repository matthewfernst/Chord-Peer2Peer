class FileWriteRspLocation:
    def __init__(self, peer_to_contact, file_id, filename, addr_hops=list()):
        self.peer_to_contact = peer_to_contact
        self.file_id = file_id
        self.filename = filename
        self.addr_hops = addr_hops

    def __repr__(self):
        return f'Peer ID {self.peer_to_contact.get_peer_id()} to store File {self.filename} as File ID {self.file_id}\n'

    def get_peer_to_contact(self):
        return self.peer_to_contact

    def get_file_id(self):
        return self.file_id

    def get_filename(self):
        return self.filename

    def get_addr_hops(self):
        return self.addr_hops
