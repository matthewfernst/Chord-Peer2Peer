import cmd
import sys

class DiscoveryNode_cmd(cmd.Cmd):
    intro = 'Talking with Discovery Node. Type help or ? to list commands.\n'
    prompt = '(DNode)'

    def __init__(self, DNode):
        super().__init__()
        self.DNode = DNode

    def do_list(self, arg):
        'List all peer nodes in chord system'
        node_list = self.DNode.get_node_dict()
        for node_id, host_port in node_list.items():
            print("NodeID {} || Host:Port {}".format(node_id, host_port))

    def do_q(self, arg):
        'terminate thread application'
        sys.exit(0)