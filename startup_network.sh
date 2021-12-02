#!/bin/bash
while getopts p:c:h: flag
do
    case "${flag}" in
        p) common_port=${OPTARG};;
        c) peer_count=${OPTARG};;
        h) discovery_host=${OPTARG};;
        *)
    esac
done

echo "Peer Count = $peer_count";
echo "Discovery Node on $discovery_host : $common_port";

peer_cnt=1
input="hosts.txt"
while IFS= read -r line
do
  hostname="${line}.cs.colostate.edu"
  # current path used to get CS EID for SSH connection (assumption is ssh-keygen is already done)
  username=$(echo "$( cd "$(dirname -- "$0")" >/dev/null 2>&1 ; pwd -P )" | awk '{split($0,a,"/"); print a[6]}')
  echo "Starting up chunk server # $peer_cnt of $peer_count on $username@$hostname"
  ssh -n "${username}@${hostname}" "cd CS555/HW2/chord_p2p/ && source set_pythonpath.sh && /usr/local/anaconda3/latest/bin/python PeerNode.py --host ${line} --port ${common_port} --dscvry_host ${discovery_host} --dscvry_port ${common_port}" &
  echo "------------------------------------------"
  if [ $peer_cnt == "$peer_count" ]; then
    break
  fi
  peer_cnt=$((peer_cnt + 1))
  sleep 5
done < "$input"