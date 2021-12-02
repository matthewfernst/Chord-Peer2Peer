class NewNodeRsp:
    def __init__(self, success, node_id=None, host_port=None ):
        self.node_id_good = success
        self.contact_id = node_id
        self.contact_host_port = host_port

    def __repr__(self):
        return f'ID::{self.node_id} {self.host_port}'

    def node_id_passed(self):
        return self.node_id_good

    def get_node_contact_id(self):
        return self.contact_id

    def get_node_contact_host_port(self):
        return self.contact_host_port
