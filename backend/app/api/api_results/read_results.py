# External imports
import traceback, json, aiofiles, asyncio
from fastapi import status
from typing import Optional
from pathlib import Path

# Internal imports
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
    sensitive_keywords
    )
from app.interface.logger_manager import setup_logger

# Initialization
logger = setup_logger(__name__, log_file_path="api", enable_debug=LOG_LEVEL_DEBUG)
manager = CommandExecutor()

# Logic
async def get_log_file_content(pid, log_type):

    try:
        data = manager.get_all_data()
        
        for program in data.get("programs", {}).values():
            for domain in program.get("domains", {}).values():
                for command in domain.get("commands", {}).values():
                    if command.get("pid") == pid:
                        log_path = command.get(log_type)
                        if log_path:

                            try:
                                with open(log_path, "r") as log_file:
                                    return {
                                        "status": True,
                                        "message": "Successfully fetched log file content",
                                        "data": {"content": log_file.read()},
                                    }
                            except Exception as e:
                                full_trace = traceback.format_exc()
                                return {
                                        "status": False,
                                        "message": "Error reading log file",
                                        "debug": {"error": str(e), "traceback": full_trace},
                                    }
                            
                        return {
                                "status_code": status.HTTP_404_NOT_FOUND,
                                "status": False,
                                "message": "Log file path not found",
                            }
        return {
                "status_code": status.HTTP_404_NOT_FOUND,
                "status": False,
                "message": "PID not found in data",
            }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        full_trace = traceback.format_exc()
        return {
                "status": False,
                "message": "Something went wrong",
                "debug": {"error": str(e), "traceback": full_trace},
            }


# ---

async def read_file(file_path: Path, limit: Optional[int] = None, offset: int = 0) -> dict:
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return {
                "status_code": status.HTTP_404_NOT_FOUND,
                "status": False,
                "message": "File not found",
            }
    if limit is not None and (not isinstance(limit, int) or limit < 0):
        return {
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "status": False,
                "message": "Limit must be a non-negative integer",
            }
    if not isinstance(offset, int) or offset < 0:
        return {
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "status": False,
                "message": "Offset must be a non-negative integer",
            }

    try:
        async with aiofiles.open(file_path, 'r') as file:
            lines = [line.strip() async for line in file]

        # Exclude first line if it's empty or whitespace
        if lines and lines[0].strip() == "":
            lines = lines[1:]

        total_lines = len(lines)
        paginated_lines = lines[offset:offset + limit] if limit is not None else lines[offset:]

        return {
            "content": paginated_lines,
            "total_lines": total_lines,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        full_trace = traceback.format_exc()

        logger.exception(f"Error reading file {file_path}: {e}")
        return {
                "status": False,
                "message": "Error reading file",
                "debug": {"error": str(e), "traceback": full_trace},
            }


# ---

async def get_domain_and_program(data: dict, target_uuid: str):
    for program_uuid, program_info in data.get("programs", {}).items():
        domains = program_info.get("domains", {})
        if target_uuid in domains:
            domain_name = domains[target_uuid].get("domain_name")
            program_name = program_info.get("program_name")
            return domain_name, program_name
    logger.warning(f"Domain ID {target_uuid} not found")
    return None, None

# ---

async def get_file_paths(target_uuid, scan_type):
    data = manager.get_all_data()
    if not data:
        return []

    domain_name, program_name = await get_domain_and_program(data, target_uuid)

    if scan_type == "subdomains":
        names = ["subdominator.txt", "bbot/subdomains.txt", "subfinder.txt", "yass.txt", "cero.txt", "sublist3r.txt", "githubsubdomains.txt", "gitlabsubdomains.txt"]
        base_dir = f"{ROOT_DATA_DIR}/{program_name}/{domain_name}/subdomains/.tmp"
    elif scan_type == "urls":
        names = ["gau.txt", "waybackurls.txt", "waymore.txt", "katana.txt", "hakrawler.txt"]
        base_dir = f"{ROOT_DATA_DIR}/{program_name}/{domain_name}/urls/.tmp"

    file_paths = []
    for name in names:
        file_paths.append(f"{base_dir}/{name}")
    
    return file_paths

# ---

async def websocket_fetch_results(target_uuid, scan_type):
    
    file_paths = await get_file_paths(target_uuid, scan_type)
    
    if not file_paths:
        logger.error(f"No file paths found for domain {target_uuid} and scan_type {scan_type}")
        return
    
    last_position = {file: 0 for file in file_paths}
    
    unique_lines = set()
    while True:
        new_lines = set()
        for file_path in last_position:
            try:
                with open(file_path, 'r') as file:
                    file.seek(last_position[file_path])
                    lines = file.readlines()
                    last_position[file_path] = file.tell()
                    new_lines.update(line.strip() for line in lines if line.strip())
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
        
        new_unique_lines = new_lines - unique_lines
        unique_lines.update(new_lines)
        
        if new_unique_lines:
            yield json.dumps(sorted(new_unique_lines))
        
        await asyncio.sleep(10)

# ---

async def http_fetch_results(target_uuid: str, file_type: str, limit: Optional[int], offset: int):
    data = manager.get_all_data()
    domain_name, program_name = await get_domain_and_program(data, target_uuid)
    if not domain_name or not program_name:
        return {
                "status_code": status.HTTP_404_NOT_FOUND,
                "status": False,
                "message": "Domain or program not found",
            }

    base_path = Path(ROOT_DATA_DIR) / program_name / domain_name
    file_mapping = {
        "urls": base_path / f"urls/{urls_file}",
        "extensions": base_path / f"urls/{extensions}",
        "live_extensions": base_path / f"urls/{live_extensions}",
        "subdomains": base_path / f"subdomains/{subdomains_file}",
        "live_subdomains": base_path / f"subdomains/{live_subdomains}",
        "httpx_subdomains": base_path / f"subdomains/{httpx_subdomains}",
        "nuclei": base_path / f"nuclei/{nuclei_file}",
        "extracted_urls": base_path / f"js/{extracted_urls}",
        "extracted_paths": base_path / f"js/{extracted_paths}",
        "sensitive_data": base_path / f"js/{sensitive_data}",
        "sensitive_keywords": base_path / f"js/{sensitive_keywords}",
        "js_nuclei": base_path / f"js/{nuclei_file}"
    }

    file_path = file_mapping.get(file_type)
    if not file_path:
        logger.error(f"Invalid file type requested: {file_type}")
        return {
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "status": False,
                "message": "Invalid file type requested",
            }

    file_data = await read_file(file_path, limit, offset)
    return {
        "status": True,
        "message": "Successfully fetched data",
        "data": {
        "domain": domain_name,
        "program": program_name,
        "content": file_data["content"],
        "total_lines": file_data["total_lines"],
        "limit": file_data["limit"],
        "offset": file_data["offset"]
    }}

# ---

async def websocket_read_results(target_uuid, scan_type):
    async for result in websocket_fetch_results(target_uuid, scan_type):
        return result

# ---

async def http_read_results(target_uuid: str, file_type: str, limit: Optional[int], offset: int):
    try:
        return await http_fetch_results(target_uuid, file_type, limit, offset)
    except Exception as e:
        full_trace = traceback.format_exc()
        logger.exception(f"Unexpected error while reading {file_type} file: {e}")
        return {
                "status": False,
                "message": f"Unexpected error while reading {file_type} file",
                "debug": {"error": str(e), "traceback": full_trace}
            }