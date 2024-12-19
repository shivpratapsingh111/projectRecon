from test_data_manager import GroupManager
data_manager_obj = GroupManager('groups.json')

group_name = "intigriti"
domain = "indeedflexx.com"
domain_uuid = "75a011e3-1e89-4656-bb1b-b13edb15789e"

command_details = {
    "command_name": "htssstpx",
    "pid": 5,
    "command": "python server.py",
    "status": "runssssssssssning",
    "start_time": "2024-01-15T10:00:00Z"
}

pid = 1
status = "2222222222222222"

data_manager_obj.update_command_status_by_pid(pid, status)