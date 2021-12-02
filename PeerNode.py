from FileReadReq import FileReadReq
from FileReadRsp import FileReadRsp
from FileTransfer import FileTransfer
from FileWriteReq import FileWriteReq
from FileWriteRspLocation import FileWriteRspLocation
from FileWriteRspSuccess import FileWriteRspSuccess
from FingerTable import FingerTable
from FingerTable import TOTAL_ENTRIES
from FingerTableReq import FingerTableReq
from FingerTableRsp import FingerTableRsp
from InPlacementReq import InPlacementReq
from InPlacementRsp import InPlacementRsp
from MoveKeysReq import MoveKeysReq
from MoveKeysRsp import MoveKeysRsp
from PeerAddress import PeerAddress
from UpdateSuccessor import UpdateSuccessor
from common_libs.TCP_Comm.ChordMsg import *
from common_libs.TCP_Comm.SerialSocket import *
from common_libs.hash_id.GenerateID import *
from common_libs.chord_msgs.NewNodeReq import *
from common_libs.chord_msgs.NodeExitReq import *
from common_libs.file.FileDataPckt import *
from common_libs.file.chord_file import *
from common_libs.chord_msgs.NackRsp import *
from random import randrange
import _thread
import signal
import threading
from common_libs.cmd_line.PeerNode_cmd import *

import copy


class PeerNode:
    REGEN_RETRY_CNT = 3
    CHECK_IN_PERIOD_SECS = 15
    RX_LOOP_TIMEOUT = 0.0

    def __init__(self, host, port, dscvry_node_host, dscvry_node_port, cmd_prompt=False, verbose=False):
        self.host = host
        self.port = port
        self.dscvry_node_host = dscvry_node_host
        self.dscvry_node_port = dscvry_node_port
        self.generate_node_id_hash()
        # self.peer_id = port % 100
        print("Peer ID is {}".format(self.peer_id))
        self.address = PeerAddress(self.peer_id, host, port)
        self.peer_dict = dict()
        self.cold_start = False
        self.awaiting_ping = dict()
        self.socket = SerialSocket(self.host, self.port)
        self.add_cmd_prompt = cmd_prompt
        self.verbose = verbose

    @classmethod
    def from_args(cls, args):
        if args.host and args.port:
            host = args.host
            port = args.port
        else:
            host = "localhost"
            port = 31810
        if args.dscvry_host and args.dscvry_port:
            dscvry_host = args.dscvry_host
            dscvry_port = args.dscvry_port
        else:
            dscvry_host = "localhost"
            dscvry_port = 31800
        return cls(host, port, dscvry_host, dscvry_port, args.cmd_prompt, verbose=args.verbose)

    def __repr__(self):
        return "{}:{}".format(str(self.host), str(self.port))

    def __str__(self):
        return f'PeerNode: ID {self.peer_id} ' + self.__repr__() + '\n'

    def get_peer_addr(self):
        return self.address

    def set_successor(self, successor):
        self.successor = successor
        self.awaiting_ping[successor.get_host_port()] = False

    def set_predecessor(self, predecessor):
        self.predecessor = predecessor
        self.awaiting_ping[predecessor.get_host_port()] = False

    def get_host_port(self):
        return f'{self.host}:{self.port}'

    def get_peer_id(self):
        return self.peer_id

    def build_finger_table(self):
        if self.cold_start:
            finger_table = FingerTable(self.address, self.successor, self.predecessor, cold_start=True, verbose=self.verbose)
            print(f"Cold Start SUCCESS for Peer ID: {self.peer_id}")
            print(finger_table)
            self.finger_table = finger_table.finger_table
            self.cold_start = False
        else:
            finger_table = FingerTable(self.address, self.successor, self.predecessor, verbose=self.verbose)
            print(f"Finger Table build SUCCESS for Peer ID: {self.peer_id}")
            print(finger_table)
            self.finger_table = finger_table.finger_table

    def exit_handler(self, signal_num, frame):
        print("peernode {} leaving network".format(self))
        exit_req = NodeExitReq(self.peer_id, self.get_host_port())
        tx_pckt = TcpPacket(ChordMsg.NODE_LEAVING_MSG, self.host, self.port, exit_req)
        try:
            tx_host_port = f'{self.dscvry_node_host}:{self.dscvry_node_port}'
            req_and_rcv_retry_sock(tx_host_port, tx_pckt, self.socket, expected_msg=ChordMsg.ACK, timeout_s=2)
            print("Pass: Communicated departure to Discovery Node")
        except Exception as e:
            print("Fail: did not communicate exit to Discovery Node due to exception {}".format(e))
        self.socket.close()
        exit(0)

    def generate_node_id_hash(self):
        self.peer_id = generate_id()

    def await_tcp_packet(self, sock):
        try:
            dfs_rx_tcp_pkt = sock.listen_and_rcv_tcp_pkt()
        except Exception:
            dfs_rx_tcp_pkt = TcpPacket(ChordMsg.NONE, self.host, self.port, None)
        return dfs_rx_tcp_pkt

    def send_neighbor_ping_req(self, neighbor_host_port):
        try:
            tx_pckt = TcpPacket(ChordMsg.PING_NEIGHBOR_REQ, self.host, self.port, None)
            to_host, to_port = getHostAndPortFromKey(neighbor_host_port)
            tx_sock = SerialSocket(to_host, to_port)
            tx_sock.connect()
            tx_sock.serialize_send_tcp_pkt(tx_pckt)
        except Exception as e:
            print("send neighbor fail {}".format(e))
            raise
        self.awaiting_ping[neighbor_host_port] = True

    def neighbor_responded(self, neighbor):
        responded = True
        if neighbor is not None:
            host_port = neighbor.get_host_port()
            if host_port != self.get_host_port():
                if not self.awaiting_ping.get(host_port):
                    try:
                        self.send_neighbor_ping_req(host_port)
                        self.awaiting_ping[host_port] = True
                    except Exception:
                        responded = False
                else:
                    responded = False
        return responded

    def check_in_on_neighbors_isr(self):
        # print("checking in on neighbors")
        pred_responded = self.neighbor_responded(self.predecessor)
        if self.predecessor != self.successor:
            succ_responded = self.neighbor_responded(self.successor)
        else:
            succ_responded = pred_responded

        if not pred_responded or not succ_responded:
            print("neighbor unresponsive need to update")
            if succ_responded:
                contact_host_port = self.successor.get_host_port()
            elif pred_responded:
                contact_host_port = self.predecessor.get_host_port()
            else:
                max_id = 2 ** TOTAL_ENTRIES
                hash_id = self.successor.get_peer_id() + 1
                if hash_id >= max_id:
                    hash_id = 0
                tx_host, tx_port = self.find_forwarded_peer(hash_id)
                contact_host_port = f'{tx_host}:{tx_port}'
            self.find_successor_and_predecessor(contact_host_port)

        threading.Timer(PeerNode.CHECK_IN_PERIOD_SECS, self.check_in_on_neighbors_isr).start()

    def send_and_rcv_new_node_ping(self):
        retry_gen_cnt = 0
        success = False
        contact_host_port = None
        while not success and retry_gen_cnt < PeerNode.REGEN_RETRY_CNT:
            try:
                host_port = f'{self.host}:{self.port}'
                req = NewNodeReq(self.peer_id, host_port)
                tx_pckt = TcpPacket(ChordMsg.NEW_NODE_REQ, self.host, self.port, req)
                tx_host_port = f'{self.dscvry_node_host}:{self.dscvry_node_port}'
                rx_pckt = req_and_rcv_retry_sock(tx_host_port, tx_pckt, self.socket, expected_msg=ChordMsg.NEW_NODE_RSP,
                                                 timeout_s=2.0)
                rsp = rx_pckt.object
                if rsp.node_id_passed():
                    contact_host_port = rsp.get_node_contact_host_port()
                    success = True
            except Exception as e:
                print("{}:{} had exception trying to ping discovery Node".format(self.host, self.port))
                success = False
            retry_gen_cnt += 1
        return success, contact_host_port

    def handle_tcp_packet(self, rx_tcp_pckt):
        if rx_tcp_pckt.msg == ChordMsg.NEW_NODE_RSP:
            self.handle_new_node_rsp(rx_tcp_pckt)
        elif rx_tcp_pckt.msg == ChordMsg.FILE_WRITE_REQ:
            self.handle_file_write_req(rx_tcp_pckt)
        elif rx_tcp_pckt.msg == ChordMsg.FILE_WRITE_RSP_SUCCESS:
            self.handle_file_write_rsp_success(rx_tcp_pckt)
        elif rx_tcp_pckt.msg == ChordMsg.FILE_READ_REQ:
            self.handle_file_read_req(rx_tcp_pckt)
        elif rx_tcp_pckt.msg == ChordMsg.FILE_READ_RSP:
            self.handle_file_read_rsp(rx_tcp_pckt)
        elif rx_tcp_pckt.msg == ChordMsg.PING_NEIGHBOR_REQ:
            self.handle_ping_neighbor_req(rx_tcp_pckt)
        elif rx_tcp_pckt.msg == ChordMsg.PING_NEIGHBOR_RSP:
            self.handle_ping_neighbor_rsp(rx_tcp_pckt)
        elif rx_tcp_pckt.msg == ChordMsg.NACK:
            self.handle_nack_rsp(rx_tcp_pckt)
        elif rx_tcp_pckt.msg == ChordMsg.FINGER_TABLE_REQ:
            self.handle_finger_table_req(rx_tcp_pckt)
        elif rx_tcp_pckt.msg == ChordMsg.IN_PLACEMENT_REQ:
            self.handle_in_placement_req(rx_tcp_pckt)
        elif rx_tcp_pckt.msg == ChordMsg.IN_PLACEMENT_RSP:
            self.handle_in_placement_rsp(rx_tcp_pckt)
        elif rx_tcp_pckt.msg == ChordMsg.UPDATE_SUCCESSOR:
            self.handle_update_success(rx_tcp_pckt)
        elif rx_tcp_pckt.msg == ChordMsg.UPDATE_FINGER_TABLE:
            self.handle_update_finger_table()
        elif rx_tcp_pckt.msg == ChordMsg.TRANSFER_FILE:
            self.handle_file_transfer(rx_tcp_pckt)
        elif rx_tcp_pckt.msg == ChordMsg.MOVE_KEYS_REQ:
            self.handle_move_keys_req(rx_tcp_pckt)
        elif rx_tcp_pckt.msg == ChordMsg.MOVE_KEYS_RSP:
            self.handle_move_keys_rsp(rx_tcp_pckt)

    def handle_new_node_rsp(self, rx_tcp_pckt):
        return

    def interface_write_req(self, filepath):

        def send_file_to_correct_peer(peer_to_contact, key, filename, binary_data):
            file_transfer_pckt = FileTransfer(self.address, key, filename, binary_data)

            print(file_transfer_pckt)
            tx_pckt = TcpPacket(ChordMsg.TRANSFER_FILE, self.host, self.port, file_transfer_pckt)
            socket = SerialSocket(peer_to_contact.get_host(), peer_to_contact.get_port())
            socket.connect()
            socket.serialize_send_tcp_pkt(tx_pckt)

        # Peer ID used for file ID for testing
        try:
            binary_data = open(filepath, 'rb').read()
            filename = os.path.basename(filepath)
            key = generate_key(filename)

            if self.in_charge_of(key):
                write_file(key, binary_data)
                print(f'Peer ID {self.peer_id} SUCCESSFULLY wrote File {filename} as Key {key}.')
            else:
                rsp_host, rsp_port = self.find_forwarded_peer(key)
                write_req_port = self.port + randrange(1, 100)

                file_write_req_pckt = FileWriteReq(self.address, key, filename, write_req_port)
                tx_pckt = TcpPacket(ChordMsg.FILE_WRITE_REQ, self.host, write_req_port, file_write_req_pckt)
                tx_host_port = f'{rsp_host}:{rsp_port}'

                write_req_socket = SerialSocket(self.host, write_req_port)
                write_req_socket.setup_continuous_listen()

                try:
                    rx_pckt = req_and_rcv_retry_sock(tx_host_port, tx_pckt, write_req_socket,
                                                     expected_msg=ChordMsg.FILE_WRITE_RSP_LOCATION, timeout_s=1)
                except (NoResponseException, UnexpectedMsgError) as e:
                    rx_pckt = None

                if rx_pckt is None:
                    raise RuntimeError("WRITE REQ SOCKET BROKEN")

                if rx_pckt is not None:
                    if self.verbose:
                        print("received {}".format(str(rx_pckt.msg)))
                    file_write_rsp_location = rx_pckt.object
                    self.print_routing_hops(file_write_rsp_location.get_addr_hops())
                    peer_to_contact = file_write_rsp_location.get_peer_to_contact()
                    send_file_to_correct_peer(peer_to_contact, key, filename, binary_data)
        except Exception as e:
            print("Unable to write file {} try again".format(e))

    def handle_file_write_req(self, rx_tcp_pckt):
        file_write_req = rx_tcp_pckt.object
        key = file_write_req.get_key()
        filename = file_write_req.get_filename()
        file_write_req.add_addr_hop(self.address)

        rsp_host = None
        rsp_port = None
        tx_pckt = None

        if self.in_charge_of(key):
            rsp_host = file_write_req.get_requesting_peer().get_host()
            rsp_port = file_write_req.get_requesting_port()

            routing_hops = file_write_req.get_addr_hops()
            file_write_rsp_location = FileWriteRspLocation(self.address, key, filename, routing_hops)
            print(file_write_rsp_location)
            tx_pckt = TcpPacket(ChordMsg.FILE_WRITE_RSP_LOCATION, self.host, self.port, file_write_rsp_location)
        else:
            rsp_host, rsp_port = self.find_forwarded_peer(key)
            tx_pckt = TcpPacket(ChordMsg.FILE_WRITE_REQ, self.host, self.port, file_write_req)

        socket = SerialSocket(rsp_host, rsp_port)
        socket.connect()
        socket.serialize_send_tcp_pkt(tx_pckt)

    def handle_file_transfer(self, rx_tcp_pckt):
        file_transfer = rx_tcp_pckt.object
        key = file_transfer.get_key()
        filename = file_transfer.get_filename()

        binary_data = file_transfer.get_binary_data()
        requesting_peer = file_transfer.get_requesting_peer()

        rsp_host = requesting_peer.get_host()
        rsp_port = requesting_peer.get_port()

        try:
            write_file(key, binary_data)
            file_write_rsp_success = FileWriteRspSuccess(self.address, key, filename)
            tx_pckt = TcpPacket(ChordMsg.FILE_WRITE_RSP_SUCCESS, self.host, self.port, file_write_rsp_success)
        except Exception as e:
            print("{} file write exception: {}".format(str(self), str(e)))
            nack_rsp = NackRsp(self.get_host_port(), ChordMsg.FILE_WRITE_REQ, e)
            tx_pckt = TcpPacket(ChordMsg.NACK, self.host, self.port, nack_rsp)

        socket = SerialSocket(rsp_host, rsp_port)
        socket.connect()
        socket.serialize_send_tcp_pkt(tx_pckt)

    def handle_file_write_rsp_success(self, rx_tcp_pckt):
        file_write_rsp_success = rx_tcp_pckt.object
        print(file_write_rsp_success)

    def interface_read_req(self, filename):
        # TODO: generate file id hash
        key = generate_key(filename)

        if self.in_charge_of(key):
            file_contents = read_file(key)
            print(
                f'READ SUCCESS on File {filename} as Key {key} from Storing Peer {self.peer_id}.')
            print(f'File Contents:\n')
            print(file_contents)
        else:
            rsp_host, rsp_port = self.find_forwarded_peer(key)
            file_read_req_pckt = FileReadReq(self.address, key, filename)
            print(file_read_req_pckt)
            tx_pckt = TcpPacket(ChordMsg.FILE_READ_REQ, self.host, self.port, file_read_req_pckt)

            socket = SerialSocket(rsp_host, rsp_port)
            socket.connect()
            socket.serialize_send_tcp_pkt(tx_pckt)

    def handle_file_read_req(self, rx_tcp_pckt):
        file_read_req = rx_tcp_pckt.object
        key = file_read_req.get_key()
        filename = file_read_req.get_filename()
        file_read_req.add_addr_hop(self.address)

        rsp_host = None
        rsp_port = None
        tx_pckt = None

        if self.in_charge_of(key):
            rsp_host = file_read_req.get_requesting_peer().get_host()
            rsp_port = file_read_req.get_requesting_peer().get_port()

            try:
                binary_data = read_file(key)
                file_read_rsp = FileReadRsp(self.address, key, filename, binary_data, file_read_req.get_addr_hops())
                tx_pckt = TcpPacket(ChordMsg.FILE_READ_RSP, self.host, self.port, file_read_rsp)

            except Exception as e:
                print("{} file read exception: {}".format(str(self), str(e)))
                nack_rsp = NackRsp(self.get_host_port(), ChordMsg.FILE_READ_REQ, e)
                tx_pckt = TcpPacket(ChordMsg.NACK, self.host, self.port, nack_rsp)

        else:
            rsp_host, rsp_port = self.find_forwarded_peer(key)
            tx_pckt = TcpPacket(ChordMsg.FILE_READ_REQ, self.host, self.port, file_read_req)

        socket = SerialSocket(rsp_host, rsp_port)
        socket.connect()
        socket.serialize_send_tcp_pkt(tx_pckt)

    def print_routing_hops(self, addr_hops):
        if addr_hops is not None:
            print("Req had {} routing jumps".format(len(addr_hops)))
            for hop in addr_hops:
                print(hop)

    def handle_file_read_rsp(self, rx_tcp_pckt):
        file_read_rsp = rx_tcp_pckt.object
        filename = file_read_rsp.get_filename()
        binary_data = file_read_rsp.get_binary_data()
        addr_hops = file_read_rsp.get_addr_hops()
        self.print_routing_hops(addr_hops)
        wr_path = f"files_back/{filename}"
        try:
            if not os.path.exists(os.path.dirname(wr_path)):
                os.makedirs(os.path.dirname(wr_path))
            with open(wr_path, "wb") as file_back:
                pickle.dump(binary_data, file_back)
            file_back.close()
        except Exception as e:
            print("unable to write the file read from chord {}".format(e))
        print(file_read_rsp)

    def handle_ping_neighbor_req(self, rx_tcp_pckt):
        tx_pckt = TcpPacket(ChordMsg.PING_NEIGHBOR_RSP, self.host, self.port, True)
        socket = SerialSocket(rx_tcp_pckt.get_response_host(), rx_tcp_pckt.get_response_port())
        socket.connect()
        socket.serialize_send_tcp_pkt(tx_pckt)

    def handle_ping_neighbor_rsp(self, rx_tcp_pckt):
        ping_rsp = rx_tcp_pckt.object
        from_host_port = f'{rx_tcp_pckt.get_response_host()}:{rx_tcp_pckt.get_response_port()}'
        self.awaiting_ping[from_host_port] = False
        succ_host_port = self.successor.get_host_port()
        pred_host_port = self.predecessor.get_host_port()
        if ping_rsp is not None and ping_rsp and (from_host_port == succ_host_port or from_host_port == pred_host_port):
            self.awaiting_ping[from_host_port] = False

    def handle_nack_rsp(self, rx_tcp_pckt):
        nack_rsp = rx_tcp_pckt.object
        print(nack_rsp)

    def in_charge_of(self, id_to_check):
        # check for when the area of a peer that is in charge wraps around
        if self.predecessor.get_peer_id() > self.peer_id:
            return (self.peer_id >= id_to_check >= 0) or \
                   (2 ** TOTAL_ENTRIES - 1 >= id_to_check > self.predecessor.get_peer_id())
        # normal check for the area a peer is in charge of
        return (self.successor.get_peer_id() == self.peer_id and self.predecessor.get_peer_id() == self.peer_id) \
               or self.peer_id >= id_to_check > self.predecessor.get_peer_id()

    def find_forwarded_peer(self, id_to_check):
        for entry in self.finger_table:
            if int(entry.get_peer_id()) >= id_to_check:
                return entry.get_host(), entry.get_port()

        return self.finger_table[0].get_host(), self.finger_table[0].get_port()

    def handle_finger_table_req(self, rx_tcp_pckt):
        finger_table_req = rx_tcp_pckt.object
        id_to_check = finger_table_req.get_id_to_check()

        # if current peer is in charge of id then the current peer is sent back to the peer asking
        # Otherwise, it moves down its finger table to find the next peer to contact
        if self.in_charge_of(id_to_check):
            rsp_host = finger_table_req.get_peer().get_host()
            rsp_port = finger_table_req.get_requesting_port()
            finger_table_rsp = FingerTableRsp(self.address)
            tx_pckt = TcpPacket(ChordMsg.FINGER_TABLE_RSP, self.host, self.port, finger_table_rsp)
        else:
            rsp_host, rsp_port = self.find_forwarded_peer(id_to_check)
            tx_pckt = TcpPacket(ChordMsg.FINGER_TABLE_REQ, rsp_host, rsp_port, finger_table_req)

        socket = SerialSocket(rsp_host, rsp_port)
        socket.connect()
        socket.serialize_send_tcp_pkt(tx_pckt)

    def send_successor_update(self, new_successor_peer):
        update_successor_pckt = UpdateSuccessor(new_successor_peer)
        tx_pckt = TcpPacket(ChordMsg.UPDATE_SUCCESSOR, self.host, self.port, update_successor_pckt)

        socket = SerialSocket(self.predecessor.get_host(), self.predecessor.get_port())
        socket.connect()
        socket.serialize_send_tcp_pkt(tx_pckt)

    def handle_in_placement_req(self, rx_tcp_pckt):
        in_placement_req = rx_tcp_pckt.object
        id_to_check = in_placement_req.get_peer_to_check().get_peer_id()

        if self.in_charge_of(id_to_check):
            rsp_host = in_placement_req.get_peer_to_check().get_host()
            rsp_port = in_placement_req.get_requesting_port()

            # for peer being placed in
            successor_to_send = copy.deepcopy(self.address)
            predecessor_to_send = copy.deepcopy(self.predecessor)

            # Contact old predecessor to update successor and rebuild its finger table
            self.send_successor_update(copy.deepcopy(in_placement_req.get_peer_to_check()))

            # updating current peer predecessor
            self.set_predecessor(copy.deepcopy(in_placement_req.get_peer_to_check()))

            # send back to requesting peer's predecessor and successor are
            in_placement_rsp = InPlacementRsp(successor_to_send, predecessor_to_send)
            tx_pckt = TcpPacket(ChordMsg.IN_PLACEMENT_RSP, self.host, self.port, in_placement_rsp)
        else:
            rsp_host, rsp_port = self.find_forwarded_peer(id_to_check)
            tx_pckt = TcpPacket(ChordMsg.IN_PLACEMENT_REQ, self.host, self.port, in_placement_req)

        socket = SerialSocket(rsp_host, rsp_port)
        socket.connect()
        socket.serialize_send_tcp_pkt(tx_pckt)

    def handle_in_placement_rsp(self, rx_tcp_pckt):

        def move_keys():
            move_keys_req = MoveKeysReq(self.address, self.successor)
            if self.verbose:
                print(move_keys_req)
            tx_pckt = TcpPacket(ChordMsg.MOVE_KEYS_REQ, self.host, self.port, move_keys_req)
            socket = SerialSocket(self.successor.get_host(), self.successor.get_port())
            socket.connect()
            socket.serialize_send_tcp_pkt(tx_pckt)

        in_placement_rsp = rx_tcp_pckt.object
        self.set_successor(in_placement_rsp.get_successor())
        self.set_predecessor(in_placement_rsp.get_predecessor())
        move_keys()

    def handle_move_keys_req(self, rx_tcp_pckt):
        move_key_req = rx_tcp_pckt.object
        rsp_host = move_key_req.get_requesting_peer().get_host()
        rsp_port = move_key_req.get_requesting_peer().get_port()
        if self.verbose:
            print(move_key_req)
        keys_to_move = {}

        for key in get_files_in_directory(get_tmp_dir_path()):
            # TODO: Remove. Only for Mac
            if key == ".DS_Store":
                continue
            if not self.in_charge_of(int(key)):
                keys_to_move[key] = read_file(key)
                remove_file(key)

        move_keys_rsp = MoveKeysRsp(keys_to_move, self.address, move_key_req.get_requesting_peer())
        tx_pckt = TcpPacket(ChordMsg.MOVE_KEYS_RSP, self.host, self.port, move_keys_rsp)
        socket = SerialSocket(rsp_host, rsp_port)
        socket.connect()
        socket.serialize_send_tcp_pkt(tx_pckt)

    def handle_move_keys_rsp(self, rx_tcp_pckt):
        move_keys_rsp = rx_tcp_pckt.object
        keys_to_store = move_keys_rsp.get_keys()

        if not keys_to_store:
            print(f"No Keys to transfer from Peer {self.successor.get_peer_id()} to Peer {self.peer_id}.")
        else:
            for key, binary_data in keys_to_store.items():
                write_file(key, binary_data)
            print(move_keys_rsp)

    def handle_update_success(self, rx_tcp_pckt):
        update_successor_req = rx_tcp_pckt.object
        self.successor = copy.deepcopy(update_successor_req.get_new_successor())
        # rebuild finger table with new successor
        self.build_finger_table()

    def find_successor_and_predecessor(self, contact_host_port):
        if contact_host_port is None:
            self.successor = copy.deepcopy(self.address)
            self.predecessor = copy.deepcopy(self.address)
            self.cold_start = True
        else:
            try:
                # port specific for finding successor and predecessor
                successor_socket_port = self.port + randrange(1, 100)
                contact_host, contact_port = getHostAndPortFromKey(contact_host_port)
                in_placement_req = InPlacementReq(self.address, successor_socket_port)
                tx_pckt = TcpPacket(ChordMsg.IN_PLACEMENT_REQ, self.host, successor_socket_port, in_placement_req)

                successor_socket = SerialSocket(self.host, successor_socket_port)
                successor_socket.setup_continuous_listen()

                rx_pckt = req_and_rcv_retry_sock(f'{contact_host}:{contact_port}', tx_pckt, successor_socket,
                                                 expected_msg=ChordMsg.IN_PLACEMENT_RSP, timeout_s=1)
            except (NoResponseException, UnexpectedMsgError) as e:
                rx_pckt = None

            if rx_pckt is not None:
                if self.verbose:
                    print("received {}".format(str(rx_pckt.msg)))
                self.handle_in_placement_rsp(rx_pckt)

    def handle_update_finger_table(self):
        self.build_finger_table()

    """ API's used for interfacing with command line terminal"""

    def get_finger_table(self):
        return self.finger_table

    def get_neighbor_str(self, neighbor):
        return f'Id {neighbor.get_peer_id()} on {neighbor.get_host_port()}'

    def print_neighbors(self):
        print(f'predecessor ' + self.get_neighbor_str(self.predecessor))
        print(f'successor ' + self.get_neighbor_str(self.successor))

    def run(self):
        self.socket.setup_continuous_listen()
        init_success, contact_host_port = self.send_and_rcv_new_node_ping()
        if init_success:
            print("Init Pass: PeerNode got ok from discovery node")
            if contact_host_port is not None:
                print("Contacting {}".format(contact_host_port))

            self.find_successor_and_predecessor(contact_host_port)
            self.build_finger_table()

            if self.add_cmd_prompt:
                peernode_cmd = PeerNode_cmd(self)
                _thread.start_new_thread(peernode_cmd.cmdloop, ())

            signal.signal(signal.SIGINT, self.exit_handler)
            self.socket.setblocking(True)
            threading.Timer(PeerNode.CHECK_IN_PERIOD_SECS, self.check_in_on_neighbors_isr).start()
            while True:
                rx_pckt = self.await_tcp_packet(self.socket)
                # print("received {}".format(str(rx_pckt.msg)))
                _thread.start_new_thread(self.handle_tcp_packet, (rx_pckt,))
                #self.handle_tcp_packet(rx_pckt)
        else:
            print("PeerNode {} failed initializations".format(self))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--dscvry_host', dest='dscvry_host', type=str)
    parser.add_argument('--dscvry_port', dest='dscvry_port', type=int)
    parser.add_argument('--host', dest='host', type=str)
    parser.add_argument('--port', dest='port', type=int)
    parser.add_argument('--cmd_prompt', dest='cmd_prompt', action='store_true')
    parser.add_argument('--verbose', dest='verbose', action='store_true')
    args = parser.parse_args()
    peer_node = PeerNode.from_args(args)
    peer_node.run()
