import numpy as np

from PeerAddress import PeerAddress
from common_libs.chord_msgs.FingerTableReq import FingerTableReq
from TCP_Comm.SerialSocket import *
from random import randrange
import copy

# Should be 16, 3 for testing purposes
TOTAL_ENTRIES = 16
FIRST_ENTRY = 0


class FingerTable:
    lookup_ports_in_use = []

    def __init__(self, peer_address, successor, predecessor, cold_start=False, verbose=False):
        self.peer_id = peer_address.get_peer_id()
        self.host = peer_address.get_host()
        self.port = peer_address.get_port()
        self.address = peer_address
        self.predecessor = predecessor
        self.successor = successor
        self.verbose = verbose
        if cold_start:
            self.finger_table = self.cold_start()
        else:
            self.finger_table = self.fill_finger_table()

    def __repr__(self):
        # numbers below come from spacing for the peer id, host, and port
        finger_table = f"\nPeerNode {self.peer_id}'s FINGER TABLE\n"
        finger_table += f"{'_' * 52}\n"
        finger_table += f"|{' ':^16}|{' ':^16}|{' ':^16}|\n"
        finger_table += f"|{'Peer ID':^16}|{'Host':^16}|{'Port':^16}|\n"
        finger_table += f"|{'_' * 16}|{'_' * 16}|{'_' * 16}|\n"
        for entry in self.finger_table:
            # 53*4 comes from taking off the top of PeerAddress's columns names
            # for printing pretty
            finger_table += str(entry)[(53*4):]
        return finger_table

    def cold_start(self):
        finger_table = np.array([PeerAddress(self.peer_id, self.host, self.port) for _ in range(TOTAL_ENTRIES)])
        return finger_table

    def get_lookup_port(self):
        lookup_socket_port = self.port + randrange(1, 100)
        while lookup_socket_port in FingerTable.lookup_ports_in_use:
            lookup_socket_port = self.port + randrange(1, 100)

        FingerTable.lookup_ports_in_use.append(lookup_socket_port)
        return lookup_socket_port

    def lookup(self, rx_host, rx_port, id_to_check):
        # initial lookup
        # port specific for lookup (random range due to multiple lookups)
        current_lookup_port = self.get_lookup_port()
        finger_table_pckt = FingerTableReq(PeerAddress(self.peer_id, self.host, self.port),
                                           id_to_check, current_lookup_port)
        tx_pckt = TcpPacket(ChordMsg.FINGER_TABLE_REQ, self.host, current_lookup_port, finger_table_pckt)

        lookup_socket = SerialSocket(self.host, current_lookup_port)
        lookup_socket.setup_continuous_listen()

        try:
            tx_host_port = f'{rx_host}:{rx_port}'
            if self.verbose:
                print("sending FINGER_TABLE_REQ to {}".format(tx_host_port))
                print("listening on {}:{}".format(self.host, current_lookup_port))
            rx_pckt = req_and_rcv_retry_sock(tx_host_port, tx_pckt, lookup_socket, retry_cnt=5,
                                             expected_msg=ChordMsg.FINGER_TABLE_RSP, timeout_s=2)
        except (NoResponseException, UnexpectedMsgError) as e:
            rx_pckt = None

        if rx_pckt is None:
            raise RuntimeError("LOOKUP IS BROKEN")

        if rx_pckt is not None:
            FingerTable.lookup_ports_in_use.remove(current_lookup_port)
            print("received {}".format(str(rx_pckt.msg)))
            finger_table_rsp = rx_pckt.object
            return finger_table_rsp.get_entry()

    def succ(self, entry):
        def check_over_shooting(calc):
            if calc >= 2 ** TOTAL_ENTRIES:
                return int(calc % (2 ** TOTAL_ENTRIES))
            else:
                return calc

        init_calc = self.peer_id + 2 ** entry
        return check_over_shooting(init_calc)

    def in_charge_of(self, id_to_check):
        # check for when the area of a peer that is in charge wraps around
        if self.predecessor.get_peer_id() > self.peer_id:
            return (self.peer_id >= id_to_check >= 0) or \
                   (2 ** TOTAL_ENTRIES - 1 >= id_to_check > self.predecessor.get_peer_id())
        # normal check for the area a peer is in charge of
        return (self.successor.get_peer_id() == self.peer_id and self.predecessor.get_peer_id() == self.peer_id) \
               or self.peer_id >= id_to_check > self.predecessor.get_peer_id()

    def fill_finger_table(self):
        finger_table = np.empty((TOTAL_ENTRIES,), dtype=PeerAddress)
        finger_table[FIRST_ENTRY] = self.successor

        for entry in range(FIRST_ENTRY + 1, TOTAL_ENTRIES):
            id_to_check = self.succ(entry)
            if self.in_charge_of(id_to_check):
                finger_table[entry] = copy.deepcopy(self.address)
            else:
                peer_to_contact = finger_table[entry - 1]
                finger_table[entry] = copy.deepcopy(
                    self.lookup(peer_to_contact.get_host(), peer_to_contact.get_port(), id_to_check))

        return finger_table
