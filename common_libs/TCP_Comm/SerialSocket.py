import socket
import pickle
import traceback
from common_libs.TCP_Comm.ChordMsg import ChordMsg
from common_libs.TCP_Comm.TcpPacket import TcpPacket
from common_libs.Error_Handling.ChordExceptions import UnexpectedMsgError, NoResponseException
import struct

MSG_SIZE_BYTE_CNT=4

def getHostAndPortFromKey(host_and_port):
    host_port_list = host_and_port.split(":")
    host = host_port_list[0]
    port = int(host_port_list[-1])
    return host, port

def req_and_rcv_retry_sock(tx_host_port, tx_pckt, rx_sock, retry_cnt=2, expected_msg=None, timeout_s=.5):
    retries = 0
    wr_rd_success = False
    retry_rx_tcp_pkt = None
    timeout_e = None
    while not wr_rd_success and retries <= retry_cnt:
        try:
            tx_host, tx_port = getHostAndPortFromKey(tx_host_port)
            tx_sock = SerialSocket(tx_host, tx_port)
            tx_sock.connect()
            tx_sock.serialize_send_tcp_pkt(tx_pckt)
            retry_rx_tcp_pkt = rx_sock.listen_and_rcv_tcp_pkt(timeout_s=timeout_s, wait_shutdown=False)
        except Exception as e:
            print("req_and_rcv_failed due to {}".format(e))
            timeout_e = e
            wr_rd_success = False

        if expected_msg and retry_rx_tcp_pkt is not None and retry_rx_tcp_pkt.msg != expected_msg:
            raise UnexpectedMsgError(expected_msg, retry_rx_tcp_pkt.msg)
        elif retry_rx_tcp_pkt is not None:
            wr_rd_success = True

        retries += 1
    if not wr_rd_success and timeout_e is None:
        raise NoResponseException(tx_sock.get_host(), tx_sock.get_port())
    return retry_rx_tcp_pkt

def req_and_rcv_retry(tx_host, tx_port, tx_pckt, rx_host, rx_port, retry_cnt=2, expected_msg=None, timeout_s=10000):
    retries = 0
    wr_rd_success = False
    retry_rx_tcp_pkt = None
    timeout_e = None
    tx_sock = None
    while not wr_rd_success and retries <= retry_cnt:
        try:
            tx_sock = SerialSocket(tx_host, tx_port)
            tx_sock.connect()
            tx_sock.serialize_send_tcp_pkt(tx_pckt, shutdown_sock=False)
            rx_sock = SerialSocket(rx_host, rx_port)
            retry_rx_tcp_pkt = rx_sock.listen_and_rcv_tcp_pkt(timeout_s=timeout_s, wait_shutdown=False)
        except Exception as e:
            timeout_e = e
            wr_rd_success = False

        if expected_msg and retry_rx_tcp_pkt is not None and retry_rx_tcp_pkt.msg != expected_msg:
            raise UnexpectedMsgError(expected_msg, retry_rx_tcp_pkt.msg)
        elif retry_rx_tcp_pkt is not None:
            wr_rd_success = True

        retries += 1
    if not wr_rd_success and timeout_e is None:
        raise NoResponseException(tx_sock.get_host(), tx_sock.get_port())
    return retry_rx_tcp_pkt


def send_msg_to_addresses(rx_host, rx_port, tx_pckt, address_dict):
    rsp_rslts = dict()
    for host_port in address_dict:
        host, port = getHostAndPortFromKey(host_port)
        try:
            rx_pckt = req_and_rcv_retry(host, port, tx_pckt, rx_host, rx_port)
            rsp_rslts[rx_pckt.get_response_host()] = rx_pckt
        except (NoResponseException, UnexpectedMsgError, Exception) as e:
            rsp_rslts[host_port] = e
    return rsp_rslts


def rcv_bytes_until_socket_close(connection):
    rcvd_bytes = bytearray()
    while True:
        chunk = connection.recv(1024)
        if not chunk:
            break
        rcvd_bytes += chunk
    return rcvd_bytes

def rcv_number_of_bytes(connection, total_byte_cnt):
    rcvd_bytes = bytearray()
    bytes_cnt_rcvd = 0
    while bytes_cnt_rcvd < total_byte_cnt:
        chunk = connection.recv(min(total_byte_cnt - bytes_cnt_rcvd, 2048))
        #if chunk == b'':
        #    raise RuntimeError("socket connection broken")
        rcvd_bytes += chunk
        bytes_cnt_rcvd = bytes_cnt_rcvd + len(chunk)
    binary = rcvd_bytes[:total_byte_cnt]
    return binary

def rcv_tcp_pckt_size(connection):
    num_bin = rcv_number_of_bytes(connection, MSG_SIZE_BYTE_CNT)
    binary_length = struct.unpack('!i', num_bin)[0]
    return binary_length

def rcv_tcp_pckt(connection):
    rx_size = rcv_tcp_pckt_size(connection)
    bytes_rcvd = rcv_number_of_bytes(connection, rx_size)
    return bytes_rcvd

def deserialize_rcv_tcp_pkt(connection, wait_shutdown=False):
    if wait_shutdown:
        bytes_rcvd = rcv_bytes_until_socket_close(connection)
    else:
        bytes_rcvd = rcv_tcp_pckt(connection)
    tcp_pkt = pickle.loads(bytes_rcvd)
    return tcp_pkt


class SerialSocket(socket.socket):
    def __init__(self, socket_host, socket_port):
        self.Host = socket_host
        self.Port = socket_port
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.continuous_listen = False

    def __str__(self):
        return "Socket Connection to : {} :: {}".format(self.Host, self.Port)

    def get_host(self):
        return self.Host

    def get_port(self):
        return self.Port

    def connect(self, **kwargs):
        return super().connect((self.Host, self.Port))

    def bind(self, **kwargs):
        return super().bind((self.Host, self.Port))

    def listen_to_port(self, listen_backlog=10):
        return super().listen(listen_backlog)

    def accept(self):
        conn, addr = super().accept()
        return conn, addr

    def serialize_send_tcp_pkt(self, tcp_packet, shutdown_sock=False):
        tcp_packet_binary = pickle.dumps(tcp_packet)
        if shutdown_sock:
            self.send_binary_stream(tcp_packet_binary, shutdown_sock)
        else:
            self.send_size_and_binary(tcp_packet_binary)

    def send_size_and_binary(self, binary_msg):
        msg_size = int(len(binary_msg))
        msg_size = struct.pack('!i', msg_size)
        self.send(msg_size)
        self.send_binary_stream(binary_msg, shutdown_sock=False)

    def send_binary_stream(self, binary_msg, shutdown_sock=True):
        total_sent = 0
        msg_size = len(binary_msg)
        while total_sent < msg_size:
            sent = self.send(binary_msg[total_sent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            total_sent += sent
        # need to inform the receiver that no more data is coming
        if shutdown_sock:
            super().shutdown(socket.SHUT_WR)
        else:
            super().close()

    def setup_continuous_listen(self, listen_backlog=10):
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind()
        self.listen_to_port(listen_backlog=listen_backlog)
        self.continuous_listen = True

    def listen_and_rcv_tcp_pkt(self, timeout_s=0.0, wait_shutdown=False):
        if timeout_s:
            self.settimeout(timeout_s)
        try:
            if not self.continuous_listen:
                self.bind()
            conn, addr = self.accept()
            listen_rx_tcp_pkt = deserialize_rcv_tcp_pkt(conn, wait_shutdown)
            conn.close()
            if not self.continuous_listen:
                self.close()
        except Exception as e:
            print("exception: {}".format(e))
            raise
        return listen_rx_tcp_pkt


if __name__ == "__main__":
    import argparse
    import time

    chunk_cnt = 24
    free_space = 16
    parser = argparse.ArgumentParser()
    parser.add_argument('--job', dest='job', type=str)
    args = parser.parse_args()

    host = "localhost"  # chunk server 'host'
    port = 31810
    list_data = [1, 2, 3, 4, 3, 2, 1]
    sock = SerialSocket(host, port)
    if args.job and args.job == "receive":
        sock.bind()
        sock.listen_to_port()
        conn, addr = sock.accept()
        print("Connected by".format(addr))
        binaryData = rcv_bytes_until_socket_close(conn)
        dataList = pickle.loads(binaryData)
        print("received {}".format(str(dataList)))
        if dataList == list_data:
            print("PASS: List received contains expected values")

    else:
        binary_list = pickle.dumps(list_data)
        sock.connect()
        sock.send_binary_stream(binary_list)
        time.sleep(.5)
        print("sent minor HeartBeat")
    print(sock)

