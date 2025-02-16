import asyncio
from app.interface.process_manager import CommandExecutor
import json
import os
from app.config.config import *
from app.logger.logger import setup_logger
from fastapi import FastAPI, HTTPException, Query
from typing import Optional
from pathlib import Path


logger = setup_logger(__name__, log_file_path='results', enable_debug=True)
manager = CommandExecutor()


async def get_log_file_content(pid, log_type):
    data = manager.get_all_data()
    
    for group in data.get("groups", {}).values():
        for domain in group.get("domains", {}).values():
            for command in domain.get("commands", {}).values():
                if command.get("pid") == pid:
                    log_path = command.get(log_type)
                    if log_path:
                        try:
                            with open(log_path, "r") as log_file:
                                return log_file.read()
                        except Exception as e:
                            return f"Error reading log file: {e}"
                    return "Log file path not found."
    
    return "PID not found in data."



async def read_file(file_path: Path, limit: Optional[int] = None, offset: int = 0) -> dict:
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

    try:
        with file_path.open('r') as file:
            lines = [line.strip() for line in file]

            # Exclude first line if it's empty or whitespace
            if lines and lines[0] == "":
                lines = lines[1:]

            total_lines = len(lines)
            paginated_lines = lines[offset:offset + limit] if limit else lines[offset:]

        return {
            "content": paginated_lines,
            "total_lines": total_lines,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.exception(f"Error reading file {file_path}: {e}")
        raise HTTPException(status_code=500, detail="Error reading file")


async def get_domain_and_group(data: dict, domain_id: str):
    for group_id, group_info in data.get("groups", {}).items():
        domains = group_info.get("domains", {})
        if domain_id in domains:
            domain_name = domains[domain_id].get("domain_name")
            group_name = group_info.get("group_name")
            return domain_name, group_name
    logger.warning(f"Domain ID {domain_id} not found")
    return None, None

async def get_file_paths(domain_id, scan_type):
    data = manager.get_all_data()
    if not data:
        return []

    domain_name, group_name = await get_domain_and_group(data, domain_id)

    if scan_type == "subdomains":
        names = ["subdominator.txt", "bbot/subdomains.txt", "subfinder.txt", "yass.txt", "cero.txt", "sublist3r.txt", "githubsubdomains.txt", "gitlabsubdomains.txt"]
        base_dir = f"{ROOT_DATA_DIR}/{group_name}/{domain_name}/subdomains/.tmp"
    elif scan_type == "urls":
        names = ["gau.txt", "waybackurls.txt", "waymore.txt", "katana.txt", "hakrawler.txt"]
        base_dir = f"{ROOT_DATA_DIR}/{group_name}/{domain_name}/urls/.tmp"

    file_paths = []
    for name in names:
        file_paths.append(f"{base_dir}/{name}")
    
    return file_paths

        
async def websocket_fetch_results(domain_id, scan_type):
    
    file_paths = await get_file_paths(domain_id, scan_type)
    
    if not file_paths:
        logger.error(f"No file paths found for domain {domain_id} and scan_type {scan_type}")
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

async def http_fetch_results(domain_id: str, file_type: str, limit: Optional[int], offset: int):
    data = manager.get_all_data()
    domain_name, group_name = await get_domain_and_group(data, domain_id)
    if not domain_name or not group_name:
        raise HTTPException(status_code=404, detail="Domain or group not found")

    base_path = Path(ROOT_DATA_DIR) / group_name / domain_name
    file_mapping = {
        "urls": base_path / f"urls/{urls_file}",
        "extensions": base_path / f"urls/{extensions}",
        "extensions_live": base_path / f"urls/{extensions_live}",
        "subdomains": base_path / f"subdomains/{subdomains_file}",
        "live_subdomains": base_path / f"subdomains/{live_subdomains}",
        "httpx_subdomains": base_path / f"subdomains/{httpx_subdomains}"
    }

    file_path = file_mapping.get(file_type)
    if not file_path:
        logger.error(f"Invalid file type requested: {file_type}")
        raise HTTPException(status_code=400, detail="Invalid file type requested")

    file_data = await read_file(file_path, limit, offset)
    return {
        "domain": domain_name,
        "group": group_name,
        "content": file_data["content"],
        "total_lines": file_data["total_lines"],
        "limit": file_data["limit"],
        "offset": file_data["offset"]
    }

async def websocket_read_results(domain_id, scan_type):
    async for result in websocket_fetch_results(domain_id, scan_type):
        return result

async def http_read_results(domain_id: str, file_type: str, limit: Optional[int], offset: int):
    return await http_fetch_results(domain_id, file_type, limit, offset)

