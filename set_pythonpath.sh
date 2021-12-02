#!/bin/bash
export CWD_PATH="$( cd "$(dirname -- "$0")" >/dev/null 2>&1 ; pwd -P )"
export PYTHONPATH="/usr/local/anaconda3/latest/lib/python3.8/site-packages"
export PYTHONPATH="$PYTHONPATH:/usr/local/pycharm-community/2020.2.3/plugins/python-ce/helpers/pydev"
export PYTHONPATH="$PYTHONPATH:/usr/local/pycharm-community/latest/plugins/python-ce/helpers/third_party/thriftpy"
export PYTHONPATH="$PYTHONPATH:/usr/local/pycharm-community/latest/plugins/python-ce/helpers/pydev"
export PYTHONPATH="$PYTHONPATH:/usr/lib64/python38.zip"
export PYTHONPATH="$PYTHONPATH:/usr/lib64/python3.8"
export PYTHONPATH="$PYTHONPATH:/usr/lib64/python3.8/lib-dynload"
export PYTHONPATH="$PYTHONPATH:/usr/lib64/python3.8/site-packages"
export PYTHONPATH="$PYTHONPATH:$CWD_PATH"
export PYTHONPATH="$PYTHONPATH:$CWD_PATH/common_libs"
export PYTHONPATH="$PYTHONPATH:$CWD_PATH/common_libs/chord_msgs"
#export PYTHONPATH="$PYTHONPATH:$CWD_PATH/common_libs/"
export PYTHONPATH="$PYTHONPATH:$CWD_PATH/common_libs/Error_Handling"
export PYTHONPATH="$PYTHONPATH:$CWD_PATH/common_libs/Finger_Table"
export PYTHONPATH="$PYTHONPATH:$CWD_PATH/common_libs/hash_id"
export PYTHONPATH="$PYTHONPATH:$CWD_PATH/common_libs/TCP_Comm"

( IFS=:
  for elem in $PYTHONPATH; do
      echo "$elem"
  done
)

py_up ()
{
  alias python='/usr/local/anaconda3/latest/bin/python'
}

py_up