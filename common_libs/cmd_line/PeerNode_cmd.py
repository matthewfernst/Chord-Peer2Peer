import cmd
import sys
from common_libs.file.FileDataPckt import *
from common_libs.chord_msgs.FileReadReq import *
from common_libs.TCP_Comm.TcpPacket import *
from common_libs.TCP_Comm.ChordMsg import *
from common_libs.TCP_Comm.SerialSocket import getHostAndPortFromKey
from common_libs.file.chord_file import *

class PeerNode_cmd(cmd.Cmd):
    intro = 'Talking with Discovery Node. Type help or ? to list commands.\n'

    def __init__(self, PeerNode):
        super().__init__()
        self.PeerNode = PeerNode
        PeerNode_cmd.prompt = str(PeerNode)

    def do_ftable(self, arg):
        'get Peer Node Finger Table'
        print(f'PeerNode {self.PeerNode.get_peer_id()} :> {self.PeerNode.get_host_port()}\n')
        self.PeerNode.build_finger_table()


    def do_neighbors(self, arg):
        'print peernodes neighbors'
        self.PeerNode.print_neighbors()

    def do_n(self, arg):
        'print peernodes neighbors'
        self.do_neighbors(arg)

    def do_list(self, arg):
        'list files on current node'
        self.do_listfiles(arg)

    def do_listfiles(self, arg):
        'list files on current node'
        file_list = get_files_in_directory(get_tmp_dir_path())
        print("files on\n{} are \n".format(self.PeerNode.get_peer_addr()))
        for file in file_list:
            print(file)
        return

    def do_rd(self, filename):
        'read file [filename]'
        self.do_readfile(filename)

    def do_readfile(self, filename):
        'readfile [filename]'
        if filename:
            self.PeerNode.interface_read_req(filename)
        else:
            print("filename needs to be provided")

    def do_wr(self, filepath):
        'write file [filepath]'
        self.do_writefile(filepath)

    def do_writefile(self, filepath):
        'write file [filepath]'
        if filepath:
            self.PeerNode.interface_write_req(filepath)
        else:
            print("filepath needs to be included")

    def do_q(self, arg):
        'terminate thread application'
        sys.exit(0)