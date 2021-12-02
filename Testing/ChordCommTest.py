from DiscoveryNode import *
from PeerNode import *
from common_libs.TCP_Comm.SerialSocket import *

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dscvry_host', dest='dscvry_host', type=str)
    parser.add_argument('--dscvry_port', dest='dscvry_port', type=int)
    parser.add_argument('--host', dest='host', type=str)
    parser.add_argument('--port', dest='port', type=int)
    parser.add_argument('--job', dest='node_type', type=str)
    parser.add_argument('--pred_host_port', dest='pred_host_port', type=str)
    parser.add_argument('--succ_host_port', dest='succ_host_port', type=str)
    args = parser.parse_args()
    if args.node_type.lower() == "peernode":
        peer_node = PeerNode.from_args(args)
        if args.pred_host_port:
            peer_node.set_predecessor(args.pred_host_port)
        if args.pred_host_port:
            peer_node.set_successor(args.succ_host_port)
        peer_node.run()
    else:
        discovery_node = DiscoveryNode.from_args(args)
        discovery_node.run()
