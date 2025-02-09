import asyncio
from app.interface.process_manager import CommandExecutor
import json
import os
from app.config.config import root_Data_Dir
from app.logger.logger import setup_logger

logger = setup_logger(__name__, log_file_path='results', enable_debug=True)
manager = CommandExecutor()

ROOT_DATA_DIR = root_Data_Dir

def get_domain_and_group(data, domain_id):
	for group_id, group_info in data["groups"].items():
		domains = group_info["domains"]
		if domain_id in domains:
			domain_name = domains[domain_id]["domain_name"]
			group_name = group_info["group_name"]
			return domain_name, group_name
	return None, None


def get_file_paths(domain_id, scan_type):
	data = manager.get_all_data()
	if not data:
		return []
	
	domain_name, group_name = get_domain_and_group(data, domain_id)
	
	urls_directory_path = f"{ROOT_DATA_DIR}/{group_name}/{domain_name}/urls"
	subdomains_directory_path = f"{ROOT_DATA_DIR}/{group_name}/{domain_name}/subdomains"
	nuclei_directory_path = f"{ROOT_DATA_DIR}/{group_name}/{domain_name}/other"
	
	if scan_type == "urls":
		file_paths=[f"{urls_directory_path}/urls.txt", f"{urls_directory_path}/urlsArrangedAll.txt", f"{urls_directory_path}/urlsArranged200.txt", f"{urls_directory_path}/urlsArranged200_small.txt"]
	
	elif scan_type == "subdomains":
		file_paths=[f"{subdomains_directory_path}/subdomains.txt", f"{subdomains_directory_path}/liveSubdomains.txt", f"{subdomains_directory_path}/httpx_subdomains.json"]
		
	elif scan_type == "nuclei":
		file_paths=[f"{nuclei_directory_path}/nuclei_results.txt"]
		
	return file_paths

		
def read_files_as_json(domain_id, scan_type):
	
	file_paths = get_file_paths(domain_id, scan_type)
	result = {}
	
	for path in file_paths:
		try:
			if not os.path.isfile(path):
				result[path] = {"error": "File not found"}
				continue

			with open(path, 'r', encoding='utf-8') as file:
				content = file.read().strip()
				if not content:
					result[path] = {"error": "File is empty"}
				else:
					result[path] = {"content": content}

		except FileNotFoundError:
			result[path] = {"error": "File not found"}
		except PermissionError:
			result[path] = {"error": "Permission denied"}
		except Exception as e:
			result[path] = {"error": str(e)}

	return result

def get_complete_results(domain_id, scan_type):
	try:
		result = read_files_as_json(domain_id, scan_type)
		return result
	except Exception as e:
		logger.debug(f"Error in getting complete results: {str(e)}")
