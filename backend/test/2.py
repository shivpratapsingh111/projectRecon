s = """
{
    "groups":
    {
        "c06506a6-0d22-49be-acaf-2dc3833c78b6":
        {
            "group_name": "test-scan-1",
            "domains":
            {
                "93b587a8-8ed6-4e33-bc5d-62a65108cfa5":
                {
                    "domain_name": "thecyberboy.com",
                    "commands":
                    {
                        "subdominator":
                        {
                            "command_name": "subdominator",
                            "pid": 208149,
                            "command": "subdominator -d thecyberboy.com",
                            "status": "completed",
                            "start_time": "07:07:52, Monday, 27-01-2025",
                            "stdout_log": "/home/retro/projectRecon-Data/test-scan-1/thecyberboy.com/subdomains/subdominator.txt",
                            "stderr_log": "/home/retro/projectRecon-Data/test-scan-1/thecyberboy.com/subdomains/logs/subdominator.txt",
                            "return_code": 0,
                            "completion_time": "07:08:09, Monday, 27-01-2025"
                        },
                        "assetfinder":
                        {
                            "command_name": "assetfinder",
                            "pid": 208146,
                            "command": "echo thecyberboy.com | assetfinder",
                            "status": "completed",
                            "start_time": "07:07:52, Monday, 27-01-2025",
                            "stdout_log": "/home/retro/projectRecon-Data/test-scan-1/thecyberboy.com/subdomains/assetfinder.txt",
                            "stderr_log": "/home/retro/projectRecon-Data/test-scan-1/thecyberboy.com/subdomains/logs/assetfinder.txt",
                            "return_code": 0,
                            "completion_time": "07:07:55, Monday, 27-01-2025"
                        }
                    }
                }
            }
        }
    }
}
"""
import json
data = json.loads(s)
id= "93b587a8-8ed6-4e33-bc5d-62a65108cfa5"
def get_domain_and_group(data, domain_id):
	for group_id, group_info in data["groups"].items():
		domains = group_info["domains"]
		if domain_id in domains:
			domain_name = domains[domain_id]["domain_name"]
			group_name = group_info["group_name"]
			return domain_name, group_name
	return None, None

print(get_domain_and_group(data, id))

# names = ["subdominator", "bbot", "subfinder", "yass", "cero"]
# file_paths = []
# group_name, domain_name = get_domain_and_group(data, id)
# for name in names:
# 	file_paths.append(f"/root/data_dir/{group_name}/{domain_name}/{name}.txt")
# print(file_paths)