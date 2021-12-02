#!/bin/bash

peer_cnt=1
input="hosts.txt"
while IFS= read -r line
do
  hostname="${line}.cs.colostate.edu"
  # current path used to get CS EID for SSH connection (assumption is ssh-keygen is already done)
  username=$(echo "$( cd "$(dirname -- "$0")" >/dev/null 2>&1 ; pwd -P )" | awk '{split($0,a,"/"); print a[6]}')
  echo "Tearing down PeerNode # $peer_cnt on $username@$hostname"
  ssh -n "${username}@${hostname}" "pkill -9 -f PeerNode.py" &
  #ssh -n "${username}@${hostname}" "ps aux | grep ${username} | grep PeerNode | awk '{print \$2}' | xargs kill -9"&
  echo "------------------------------------------"
  peer_cnt=$((peer_cnt + 1))
done < "$input"
