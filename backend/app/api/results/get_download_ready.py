from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
from app.interface.process_manager import CommandExecutor
import zipfile, time
from app.config.config import ROOT_DATA_DIR
from app.logger.logger import setup_logger
import threading
from app.config.config import *
import asyncio

logger = setup_logger(__name__, log_file_path='download', enable_debug = True)
manager = CommandExecutor()


async def get_domain_and_program(data, target_uuid):
	for program_uuid, program_info in data["programs"].items():
		domains = program_info["domains"]
		if target_uuid in domains:
			domain_name = domains[target_uuid]["domain_name"]
			program_name = program_info["program_name"]
			return domain_name, program_name
	return None, None


async def create_directory_archive(directory_path):
    if not os.path.isdir(directory_path):
        raise ValueError(f"The directory {directory_path} does not exist or is not a valid directory.")
    
    archive_name = f"{os.path.basename(directory_path)}.zip"
    archive_path = os.path.join(os.getcwd(), archive_name)

    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, directory_path))

    threading.Thread(target=asyncio.run, args=(delete_archive_after_delay(archive_path, 30),), daemon=True).start()

    return FileResponse(archive_path, media_type='application/zip', filename=os.path.basename(archive_path))

async def delete_archive_after_delay(archive_path, delay=30):
    await asyncio.sleep(delay)
    if os.path.exists(archive_path):
        os.remove(archive_path)
        print(f"Deleted archive: {archive_path}")
    else:
        print(f"Archive not found for deletion: {archive_path}")



async def get_program_scan(program_name):
	program_path = f"{ROOT_DATA_DIR}/{program_name}"
	return await create_directory_archive(program_path)
 
async def get_download(target_uuid, file_name):
	data = manager.get_all_data()

	domain_name, program_name = await get_domain_and_program(data, target_uuid)
	
	urls_directory_path = f"{ROOT_DATA_DIR}/{program_name}/{domain_name}/urls"
	subdomains_directory_path = f"{ROOT_DATA_DIR}/{program_name}/{domain_name}/subdomains"
	nuclei_directory_path = f"{ROOT_DATA_DIR}/{program_name}/{domain_name}/nuclei"
	js_directory_path = f"{ROOT_DATA_DIR}/{program_name}/{domain_name}/js"
	file_path = None
	if file_name == "subdomains":
		file_path=f"{subdomains_directory_path}/{subdomains_file}"
	elif file_name == "live-subdomains":
		file_path=f"{subdomains_directory_path}/{live_subdomains}"
	elif file_name == "httpx-subdomains":
		file_path=f"{subdomains_directory_path}/{httpx_subdomains}"
	elif file_name == "urls":
		file_path=f"{urls_directory_path}/{urls_file}"
	elif file_name == "extensions":
		file_path=f"{urls_directory_path}/{extensions}"
	elif file_name == "live-extensions":
		file_path=f"{urls_directory_path}/{live_extensions}"
	elif file_name == "nuclei":
		file_path=f"{nuclei_directory_path}/{nuclei_file}"
	elif file_name == "js-nuclei":
		file_path=f"{js_directory_path}/{nuclei_file}"
	elif file_name == "extracted-urls":
		file_path=f"{js_directory_path}/{extracted_urls}"
	elif file_name == "extracted-paths":
		file_path=f"{js_directory_path}/{extracted_paths}"
	elif file_name == "sensitive-data":
		file_path=f"{js_directory_path}/{sensitive_data}"
	elif file_name == "sensitive-keywords":
		file_path=f"{js_directory_path}/{sensitive_keywords}"

	try:
		if file_path and os.path.exists(file_path):
			return FileResponse(file_path, filename=file_path.split("/")[-1])
		else:
			return "Log file not found"
	except Exception as e:
		logger.exception(f"Error: {str(e)}")
		raise HTTPException(status_code=404, detail="Domain ID or command name not found")