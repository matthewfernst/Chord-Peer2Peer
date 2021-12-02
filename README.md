# Chord Peer 2 Peer System
Chord Peer 2 Peer System

Help is provided for any questions that you have about running the command line options.  command prompt is optional for receiving input from user
Note: the port and host for the DiscoveryNode need to be the same

Before running any node you need to source the python environment by running
source ./set_pythonpath.sh

PeerNode
python PeerNode.py --host raleigh --port 9320 --dscvry_host tokyo --dscvry_port 9100 --cmd_prompt

Discovery Node 
python DiscoveryNode.py --host tokyo --port 9100

to run multiple peers on different machines you can run
./startup_network.sh -p 25000 -c 4 -h tokyo
-h is the host of the DiscoveryNode
-c is the number of different peers you want to run
-p is the port of the DiscoveryNode and is used for the port of the PeerNodes
