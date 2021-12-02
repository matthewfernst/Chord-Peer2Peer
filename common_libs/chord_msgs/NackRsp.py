
class NackRsp:
    def __init__(self, host_port_with_err, msg_nacked, error):
        self.err_host_port = host_port_with_err
        self.msg_nacked = msg_nacked
        self.error = error

    def __repr__(self):
        return f'{self.msg_nacked} NACKED from {self.err_host_port} due to error: \n{self.error}'

    def get_msg_nacked(self):
        return self.msg_nacked

    def get_host_port_with_err(self):
        return self.err_host_port

    def get_error(self):
        return self.error
