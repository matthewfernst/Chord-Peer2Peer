from enum import Enum, unique


@unique
class ChordMsg(Enum):
    NONE = 0
    NEW_NODE_REQ = 1
    NEW_NODE_RSP = 2
    NODE_LEAVING_MSG = 3
    FILE_WRITE_REQ = 4
    FILE_WRITE_RSP_LOCATION = 5
    FILE_WRITE_RSP_SUCCESS = 6
    FILE_READ_REQ = 7
    FILE_READ_RSP = 8
    PING_NEIGHBOR_REQ = 9
    PING_NEIGHBOR_RSP = 10
    FINGER_TABLE_REQ = 11
    FINGER_TABLE_RSP = 12
    ACK = 13
    NACK = 14
    IN_PLACEMENT_REQ = 15
    IN_PLACEMENT_RSP = 16
    UPDATE_SUCCESSOR = 17
    UPDATE_FINGER_TABLE = 18
    TRANSFER_FILE = 19
    MOVE_KEYS_REQ = 20
    MOVE_KEYS_RSP = 21

    def __str__(self):
        return "CHORD_MSG."+self.name + "(" + str(self.value) + ")"
