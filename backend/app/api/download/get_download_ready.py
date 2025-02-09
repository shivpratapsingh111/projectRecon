from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
from app.interface.process_manager import CommandExecutor
import zipfile, time
from app.config.config import root_Data_Dir
from app.logger.logger import setup_logger
import threading

ROOT_DATA_DIR = root_Data_Dir
logger = setup_logger(__name__, log_file_path='download', enable_debug = True)
manager = CommandExecutor()


def get_domain_and_group(data, domain_id):
	for group_id, group_info in data["groups"].items():
		domains = group_info["domains"]
		if domain_id in domains:
			domain_name = domains[domain_id]["domain_name"]
			group_name = group_info["group_name"]
			return domain_name, group_name
	return None, None


def create_directory_archive(directory_path):
    # Ensure the provided directory exists
    if not os.path.isdir(directory_path):
        raise ValueError(f"The directory {directory_path} does not exist or is not a valid directory.")
    
    # Create a zip file name from the directory name
    archive_name = f"{os.path.basename(directory_path)}.zip"
    
    # Path where the archive will be saved
    archive_path = os.path.join(os.getcwd(), archive_name)
    
    # Create a zip archive of the directory
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Add file to the archive with relative path
                zipf.write(file_path, os.path.relpath(file_path, directory_path))
    threading.Thread(target=delete_archive_after_delay, args=(archive_path,), daemon=True).start()

    # Return the path of the archive
    return FileResponse(archive_path, media_type='application/zip', filename=os.path.basename(archive_path))

def delete_archive_after_delay(archive_path, delay=10):
    time.sleep(delay)
    if os.path.exists(archive_path):
        os.remove(archive_path)
        print(f"Deleted archive: {archive_path}")
    else:
        print(f"Archive not found for deletion: {archive_path}")



def get_group_scan(group_name):
	group_path = f"{ROOT_DATA_DIR}/{group_name}"
	return create_directory_archive(group_path)
 
def get_download(domain_id, file_name):
	data = manager.get_all_data()

	domain_name, group_name = get_domain_and_group(data, domain_id)
	
	urls_directory_path = f"{ROOT_DATA_DIR}/{group_name}/{domain_name}/urls"
	subdomains_directory_path = f"{ROOT_DATA_DIR}/{group_name}/{domain_name}/subdomains"
	nuclei_directory_path = f"{ROOT_DATA_DIR}/{group_name}/{domain_name}/other"
	file_path = None
	if file_name == "subdomains":
		file_path=f"{subdomains_directory_path}/subdomains.txt"
	elif file_name == "liveSubdomains":
		file_path=f"{subdomains_directory_path}/liveSubdomains.txt"
	elif file_name == "httpx_subdomains":
		file_path=f"{subdomains_directory_path}/httpx_subdomains.json"
	elif file_name == "urls":
		file_path=f"{urls_directory_path}/urls.txt"
	elif file_name == "urlsArrangedAll":
		file_path=f"{urls_directory_path}/urlsArrangedAll.txt"
	elif file_name == "urlsArranged200":
		file_path=f"{urls_directory_path}/urlsArranged200.txt"
	elif file_name == "urlsArranged200_small":
		file_path=f"{urls_directory_path}/urlsArranged200_small.txt"
	elif file_name == "nuclei_results":
		file_path=f"{nuclei_directory_path}/nuclei_results.txt"

	try:
		if file_path and os.path.exists(file_path):
			return FileResponse(file_path, filename=file_path.split("/")[-1])
		else:
			return "Log file not found"
	except Exception as e:
		logger.exception(f"Error: {str(e)}")
		raise HTTPException(status_code=404, detail="Domain ID or command name not found")