class TcpPacket:
    def __init__(self, msg, rsp_host, rsp_port, dfs_object):  # (non-privileged ports are > 1023)
        self.msg = msg
        self.rsp_host = rsp_host
        self.rsp_port = rsp_port
        self.object = dfs_object

    def __repr__(self):
        return "msg: " + str(self.msg) + "\n" + \
            "object: " + str(self.object)

    def __eq__(self, other):
        is_equal = False
        if isinstance(other, TcpPacket):
            is_equal = self.object == other.object
        return is_equal

    def get_response_host(self):
        return self.rsp_host

    def get_response_port(self):
        return self.rsp_port
