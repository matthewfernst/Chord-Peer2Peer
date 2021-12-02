from common_libs.hash_id.GenerateID import generate_key
import os
class FileDataPckt:
    def __init__(self, file_id, file_name, binary_data):
        self.file_id = file_id
        self.file_name = file_name
        self.binary_data = binary_data

    @classmethod
    def load_file(cls, filepath):
        try:
            with open(filepath, "rb") as file_h:
                file_binary = file_h.read()
                file_h.close()
        except Exception as e:
            print("unable to read file to write {}".format(e))
            file_h.close()
            return None
        file_name = os.path.basename(filepath)
        file_id = generate_key((file_name))
        return cls(file_id, file_name, file_binary)

    def __repr__(self):
        return f'{self.file_name} FILEID::{self.file_id}'

    def get_file_id(self):
        return self.file_id

    def get_binary_data(self):
        return self.binary_data
