import time
import hashlib

MAX_ID_INT = int(0xFFFF)

def generate_id():
    time_stamp = time.time().hex().encode('utf-8')
    hash = hashlib.md5(time_stamp)
    hash_id_bytes = (hash.digest())[0:3]
    hash_id_int = int.from_bytes(hash_id_bytes, "little") & 0xFFFF
    return hash_id_int


def generate_key(filename):
    hash = hashlib.md5(filename.encode('utf-8'))
    hash_id_bytes = (hash.digest())[0:3]
    hash_id_int = int.from_bytes(hash_id_bytes, "little") & 0xFFFF
    return hash_id_int

if __name__ == "__main__":
    for cnt in range(0,40):
        time.sleep(.25)
        print(generate_id())