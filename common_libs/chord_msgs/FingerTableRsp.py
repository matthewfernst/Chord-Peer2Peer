class FingerTableRsp:
    def __init__(self, entry):
        self.entry = entry

    def __repr__(self):
        return f'Entry returned::{self.entry}'

    def get_entry(self):
        return self.entry

