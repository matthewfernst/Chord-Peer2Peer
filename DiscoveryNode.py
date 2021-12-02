from common_libs.TCP_Comm.ChordMsg import *
from common_libs.TCP_Comm.SerialSocket import *
from common_libs.chord_msgs.NewNodeReq import *
from common_libs.chord_msgs.NewNodeRsp import *
from common_libs.chord_msgs.NodeExitReq import *
from common_libs.Error_Handling.ChordExceptions import *
from common_libs.file.FileDataPckt import *
from common_libs.file.chord_file import *
from common_libs.cmd_line.DiscoveryNode_cmd import *
import _thread
import random
import signal

class DiscoveryNode:
    def __init__(self, host, port, generate_id=None):  # (non-privileged ports are > 1023)
        self.host = host
        self.port = port
        self.generate_id = generate_id
        self.node_dict = dict()
        self.socket = SerialSocket(self.host, self.port)

    @classmethod
    def from_args(cls, args):
        if args.host and args.port:
            host = args.host
            port = args.port
        else:
            host = "localhost"
            port = 31800
        return cls(host, port)

    def __repr__(self):
        return "{}:{}".format(str(self.host), str(self.port))

    def get_node_dict(self):
        return self.node_dict

    def rm_node_from_dict(self, node_id):
        try:
            self.node_dict.pop(node_id)
        except Exception as e:
            print("Failed to pop: {} from the following dict {} due to exception \n{}".format(node_id, self.node_dict, e))
        return

    def exit_handler(self, signal_num, frame):
        print("discovery Node {} leaving network".format(self))
        self.socket.close()
        exit(0)

    def add_node_to_dict(self, new_node_msg):
        node_id_good = True
        host_port = new_node_msg.get_host_port()
        node_id = new_node_msg.get_node_id()
        if not self.node_dict.get(node_id):
            cntct_hash_id, cntct_host_port = self.get_random_node_from_dict()
            self.node_dict[node_id] = host_port
        else:
            node_id_good = False
            cntct_hash_id = None
            cntct_host_port = None
        rsp = NewNodeRsp(node_id_good, node_id=cntct_hash_id, host_port=cntct_host_port)
        return rsp

    def get_random_node_from_dict(self):
        if len(self.node_dict):
            hash_id_key, host_port = random.choice(list(self.node_dict.items()))
        else:
            hash_id_key = None
            host_port = None
        return hash_id_key, host_port

    def await_tcp_packet(self, sock):
        dfs_rx_tcp_pkt = sock.listen_and_rcv_tcp_pkt(wait_shutdown=False)
        return dfs_rx_tcp_pkt

    def handle_tcp_packet(self, rx_tcp_pckt):
        if rx_tcp_pckt.msg == ChordMsg.NEW_NODE_REQ:
            self.handle_new_node_msg(rx_tcp_pckt)
        elif rx_tcp_pckt.msg == ChordMsg.NODE_LEAVING_MSG:
            self.handle_node_leaving_msg(rx_tcp_pckt)
        elif rx_tcp_pckt.msg == ChordMsg.NACK:
            self.handle_nack_rsp(rx_tcp_pckt)

    def handle_new_node_msg(self, rx_tcp_pckt):
        new_node_msg = rx_tcp_pckt.object
        if isinstance(new_node_msg, NewNodeReq):
            rsp_host, rsp_port = getHostAndPortFromKey(new_node_msg.get_host_port())
            rsp_pckt = self.add_node_to_dict(new_node_msg)
            tx_pckt = TcpPacket(ChordMsg.NEW_NODE_RSP, self.host, self.port, rsp_pckt)
        else:
            rsp_host = rx_tcp_pckt.get_response_host()
            rsp_port = rx_tcp_pckt.get_response_port()
            tx_pckt = TcpPacket(ChordMsg.NACK, self.host, self.port, UnexpectedMsgObjectError(NewNodeReq, type(new_node_msg)))
        socket = SerialSocket(rsp_host, rsp_port)
        socket.connect()
        socket.serialize_send_tcp_pkt(tx_pckt)

    def handle_node_leaving_msg(self, rx_tcp_pckt):
        node_leaving_msg = rx_tcp_pckt.object
        if isinstance(node_leaving_msg, NodeExitReq):
            self.rm_node_from_dict(node_leaving_msg.get_node_id())
            rsp_host, rsp_port = getHostAndPortFromKey(node_leaving_msg.get_host_port())
            tx_pckt = TcpPacket(ChordMsg.ACK, self.host, self.port, None)
        else:
            rsp_host = rx_tcp_pckt.get_response_host()
            rsp_port = rx_tcp_pckt.get_response_port()
            tx_pckt = TcpPacket(ChordMsg.NACK, self.host, self.port, UnexpectedMsgObjectError(NodeExitReq, type(node_leaving_msg)))
        try:
            socket = SerialSocket(rsp_host, rsp_port)
            socket.connect()
            socket.serialize_send_tcp_pkt(tx_pckt)
        except Exception as e:
            print(e)

    def handle_nack_rsp(self, rx_tcp_pckt):
        nack_rsp = rx_tcp_pckt.object
        print(nack_rsp)

    def run(self):
        print("Running Discovery Node {}".format(str(self)))
        Dnode_cmd = DiscoveryNode_cmd(self)
        signal.signal(signal.SIGINT, self.exit_handler)
        _thread.start_new_thread(Dnode_cmd.cmdloop, ())
        self.socket.setup_continuous_listen()
        while True:
            rx_pckt = self.await_tcp_packet(self.socket)
            print("received {}".format(str(rx_pckt.msg)))
            self.handle_tcp_packet(rx_pckt)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', dest='host', type=str)
    parser.add_argument('--port', dest='port', type=int)
    args = parser.parse_args()
    discovery_node = DiscoveryNode.from_args(args)
    discovery_node.run()