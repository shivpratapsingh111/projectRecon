from backend.app.interface.json_data_manager import GroupManager
from app.config.config import *
# data_manager_obj = GroupManager(data_file)

# import json
# with open('groups.json') as f:
#     data = json.load(f)

# for group_uuid in data['groups']:
#     print(group_uuid)

# # print(data_manager_obj._read_file())
# import backend.app.services.scans.arrange_urls
# # Get the file path of the module
# module_path = backend.app.services.scans.arrange_urls.__file__

# print(f"python3 {module_path}")

from app.interface.process_manager import CommandExecutor

a= CommandExecutor()

a._update_process_status(544429, "killed")








# from test_data_manager import GroupManager
# data_manager_obj = GroupManager('groups.json')
# group_name = "intigriti"
# domain = "indeedflexx.com"
# domain_uuid = "75a011e3-1e89-4656-bb1b-b13edb15789e"

# command_details = {
#     "command_name": "htssstpx",
#     "pid": 5,
#     "command": "python server.py",
#     "status": "runssssssssssning",
#     "start_time": "2024-01-15T10:00:00Z"
# }

# pid = 1
# status = "2222222222222222"

# data_manager_obj.update_command_status_by_pid(pid, status)