# External Imports
import os
import traceback
import zipfile
import threading
import asyncio
from typing import Dict, Any
from fastapi import status

# Local Imports
from app.interface.process_manager import CommandExecutor
from app.config.config import (
    LOG_LEVEL_DEBUG,
    ROOT_DATA_DIR,
    urls_file,
    extensions,
    live_extensions,
    subdomains_file,
    live_subdomains,
    httpx_subdomains,
    nuclei_file,
    extracted_urls,
    extracted_paths,
    sensitive_data,
    sensitive_keywords,
)
from app.logger.logger import setup_logger

# Initialization
logger = setup_logger(
    __name__, log_file_path="api_results", enable_debug=LOG_LEVEL_DEBUG
)
manager = CommandExecutor()


# Logic
async def get_domain_and_program(data: Dict[str, Any], target_uuid: str) -> str:
    for program_uuid, program_info in data["programs"].items():
        domains = program_info["domains"]
        if target_uuid in domains:
            domain_name = domains[target_uuid]["domain_name"]
            program_name = program_info["program_name"]
            return domain_name, program_name
    return None, None


# ---


async def create_directory_archive(directory_path: str) -> Dict[str, Any]:
    if not os.path.isdir(directory_path):
        return {
            "status_code": status.HTTP_404_NOT_FOUND,
            "status": False,
            "message": "Program data not found",
            "debug": {
                "error": f"The directory '{directory_path}' does not exist or is not a valid directory"
            },
        }
    try:
        archive_name = f"{os.path.basename(directory_path)}.zip"
        archive_path = os.path.join(os.getcwd(), archive_name)

        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, directory_path))

        threading.Thread(
            target=asyncio.run,
            args=(delete_archive_after_delay(archive_path, 30),),
            daemon=True,
        ).start()

        return {
            "status": True,
            "message": "Archive created successfully",
            "data": {"archive_path": archive_path},
        }
    
    except Exception as e:
        full_trace = traceback.format_exc()
        logger.exception("Error in creating archive of scan results")
        return {
            "status": False,
            "message": "Error in creating archive of scan results",
            "debug": {"error": str(e), "traceback": full_trace},
            "data": {"id": None},
        }

# ---

async def delete_archive_after_delay(archive_path, delay=30):
    await asyncio.sleep(delay)
    if os.path.exists(archive_path):
        os.remove(archive_path)
        logger.debug(f"Deleted archive: {archive_path}")
    else:
        logger.debug(f"Archive not found for deletion: {archive_path}")

# ---

async def get_program_scan_results(program_name: str) -> Dict[str, Any]:

    try:
        program_path = f"{ROOT_DATA_DIR}/{program_name}"
        return await create_directory_archive(program_path)
    except Exception as e:
        full_trace = traceback.format_exc()
        logger.exception(f"Unexpected error: {e}")
        return {
            "status": False,
            "message": "Internal server error",
            "debug": {"error": str(e), "traceback": full_trace},
        }

# ---

async def get_download(target_uuid: str, file_name: str) -> Dict[str, Any]:
    try:
        data = manager.get_all_data()
        domain_name, program_name = await get_domain_and_program(data, target_uuid)

        base_path = f"{ROOT_DATA_DIR}/{program_name}/{domain_name}"
        file_map = {
            "subdomains": f"{base_path}/subdomains/{subdomains_file}",
            "live-subdomains": f"{base_path}/subdomains/{live_subdomains}",
            "httpx-subdomains": f"{base_path}/subdomains/{httpx_subdomains}",
            "urls": f"{base_path}/urls/{urls_file}",
            "extensions": f"{base_path}/urls/{extensions}",
            "live-extensions": f"{base_path}/urls/{live_extensions}",
            "nuclei": f"{base_path}/nuclei/{nuclei_file}",
            "js-nuclei": f"{base_path}/js/{nuclei_file}",
            "extracted-urls": f"{base_path}/js/{extracted_urls}",
            "extracted-paths": f"{base_path}/js/{extracted_paths}",
            "sensitive-data": f"{base_path}/js/{sensitive_data}",
            "sensitive-keywords": f"{base_path}/js/{sensitive_keywords}",
        }

        file_path = file_map.get(file_name)

        if file_path and os.path.exists(file_path):
            return {
                "status": True,
                "message": "File found",
                "data": {
                    "log_file_path": file_path,
                    "filename": os.path.basename(file_path),
                }
            }
        else:
            return {
                "status_code": status.HTTP_404_NOT_FOUND,
                "status": False,
                "message": "Log file not found",
                "debug": {"file_name": file_name, "resolved_path": file_path}
            }

    except Exception as e:
        full_trace = traceback.format_exc()
        logger.exception(f"Unexpected error: {e}")
        return {
            "status": False,
            "message": "Internal server error",
            "debug": {"error": str(e), "traceback": full_trace},
        }