
class UnexpectedMsgError(Exception):
    def __init__(self, expected_msg, rcvd_msg):
        self.message = f'UnexpectedMsgError: expected: {expected_msg} received: {rcvd_msg}'
        super(UnexpectedMsgError, self).__init__(self.message)

    def __str__(self):
        return self.message

class UnexpectedMsgObjectError(Exception):
    def __init__(self, expected_clss, rcvd_clss):
        self.message = f'UnexpectedMsgObjectError: expected: {expected_clss} received: {rcvd_clss}'
        super(UnexpectedMsgObjectError, self).__init__(self.message)

    def __str__(self):
        return self.message

class NoResponseException(Exception):
    def __init__(self, host, port):
        self.message = f'No Response from {host} Port: {port}'
        super(NoResponseException, self).__init__(self.message)

    def __str__(self):
        return self.message

class ExceptionWrapper(Exception):
    def __init__(self, exception_str, additional_info):
        self.message = exception_str + additional_info
        super().__init__(self.message)

    def __str__(self):
        return self.message
