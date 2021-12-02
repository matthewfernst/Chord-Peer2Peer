from common_libs.TCP_Comm.SerialSocket import *
from UpdateFingerTable import UpdateFingerTable
update_finger_table_pckt = UpdateFingerTable()

tx_pckt = TcpPacket(ChordMsg.UPDATE_FINGER_TABLE, "localhost", 9111, update_finger_table_pckt)

socket = SerialSocket("localhost", 9007)
socket.connect()
socket.serialize_send_tcp_pkt(tx_pckt)

print("DONE")
