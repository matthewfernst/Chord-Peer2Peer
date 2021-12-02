from PeerAddress import PeerAddress
from common_libs.TCP_Comm.SerialSocket import *
from FileWriteReq import FileWriteReq
localhost = "localhost"
address = f"{'_' * 52}\n"
address += f"|{' ':^16}|{' ':^16}|{' ':^16}|\n"
address += f"|{'Peer ID':^16}|{'Host':^16}|{'Port':^16}|\n"
address += f"|{'_' * 16}|{'_' * 16}|{'_' * 16}|\n"
address += f"|{' ':^16}|{' ':^16}|{' ':^16}|\n"
address += f"|{7:^16}|{localhost:^16}|{9007:^16}|\n"
address += f"|{'_' * 16}|{'_' * 16}|{'_' * 16}|\n"


print(address[53*4:])





