@echo off
set CURR_DIR=%~dp0
set PYTHONPATH=%CURR_DIR%common_libs;%CURR_DIR%common_libs\chord_msgs;%CURR_DIR%common_libs\Error_Handling;%CURR_DIR%common_libs\Finger_Table;%CURR_DIR%common_libs\hash_id;%CURR_DIR%common_libs\TCP_Comm;
echo PYTHONPATH=%PYTHONPATH%