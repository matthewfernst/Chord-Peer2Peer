import random
import pickle
import os
import platform
from os import listdir
from os.path import isfile, join
from common_libs.hash_id.GenerateID import *


def get_file_location(file_id):
    return get_tmp_dir_path()+f'{file_id}'


def get_tmp_dir_path():
    tmp_location = "/tmp/gladmatt/"
    # for mac testing
    if platform.system() == "Darwin":
        tmp_location = "/Users/matthewernst/chord_p2p/tmp/"
    elif os.name == 'nt':
        tmp_location = "C:\\tmp\\"
    return tmp_location


def list_any_out_of_range(int_list, low_id, high_id):
    return any((x > high_id or x < low_id) for x in int_list)

def get_file_ids_in_range(low_file_id, high_file_id):
    dir_path = get_tmp_dir_path()
    file_id_list = get_files_in_directory(dir_path)
    file_id_list = [int(elem) for elem in file_id_list]
    id_match_list = [elem for elem in file_id_list if elem >= low_file_id and elem <= high_file_id]
    return id_match_list

def get_files_in_directory(dir_path):
    if not os.path.exists(os.path.dirname(dir_path)):
        os.makedirs(os.path.dirname(dir_path))
    return [f for f in listdir(dir_path) if isfile(join(dir_path, f))]

def write_file(file_id, file_bin):
    # TODO: Need to check for collisions
    wr_path = get_file_location(file_id)
    if not os.path.exists(os.path.dirname(wr_path)):
        os.makedirs(os.path.dirname(wr_path))
    with open(wr_path, "wb") as file_h:
        pickle.dump(file_bin, file_h)
    file_h.close()

def read_file(file_id):
    rd_path = get_file_location(file_id)
    with open(rd_path, "rb") as file_h:
        file_binary = file_h.read()
    file_h.close()
    return pickle.loads(file_binary)

def test_get_file_ids_in_range(iterations=40):
    test_passed = True
    print("running {} test iterations of get_file_ids_in_range".format(iterations))
    for cnt in range(0, iterations):
        max_id = random.randint(1, MAX_ID_INT)
        min_id = random.randint(1, max_id)
        file_ids = get_file_ids_in_range(min_id, max_id)
        is_out_of_range = list_any_out_of_range(file_ids, min_id, max_id)
        if is_out_of_range:
            test_passed = False
            print("Fail: value > {} and value < {} in list \n{}".format(max_id, min_id, file_ids))

    if test_passed:
        print("PASSED")
    return test_passed


def test_write_and_read_random_files(iterations=20, max_file_size_bytes=64000):
    import tempfile
    test_passed = True
    print("running {} test iterations of write and read random files".format(iterations))
    for cnt in range(0, iterations):
        tf = tempfile.NamedTemporaryFile()
        file_name = tf.name
        size_bytes = random.randint(1, max_file_size_bytes)
        wr_data_bytes = bytearray(random.getrandbits(8) for _ in range(size_bytes))
        file_id = generate_key(file_name)
        write_file(file_id, wr_data_bytes)
        rd_data_bytes = read_file(file_id)
        if rd_data_bytes != wr_data_bytes:
            test_passed = False
            print("FAIL: file {} bytes_read from bytes_written don't match".format(file_id))
    if test_passed:
        print("PASSED")
    return test_passed

def remove_file(file_id, dirPath=get_tmp_dir_path()):
    os.remove(join(dirPath, file_id))

def remove_temp_files():
    dir = get_tmp_dir_path()
    for file in listdir(dir):
        try:
            os.remove(join(dir, file))
        except:
            print("couldn't delete file {}".format(file))


if __name__ == "__main__":
    test_write_and_read_random_files(iterations=20, max_file_size_bytes=12000)
    test_get_file_ids_in_range(iterations=30)
    remove_temp_files()