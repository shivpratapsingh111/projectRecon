import asyncio
from app.interface.process_manager import CommandExecutor
import json
import os

from app.logger.logger import setup_logger

logger = setup_logger(__name__, log_file_path='results', enable_debug=True)
manager = CommandExecutor()

def get_file_paths(domain_id, manager, scan_type):
    data = manager.get_all_data()
    if not data:
        return []

    scan_types = {
        'subdomains': ["subfinder", "assetfinder", "subdominator"],
        'urls': ["waybackurls", "gau", "waymore", "hakrawler", "katana"]
    }

    filepath_list = scan_types.get(scan_type)
    if not filepath_list:
        logger.error(f"Invalid scan_type provided: {scan_type}")
        return []

    file_paths = []
    for group in data.get("groups", {}).values():
        domain = group.get("domains", {}).get(domain_id)
        if domain:
            commands = domain.get("commands", {})
            for cmd in filepath_list:
                log_path = commands.get(cmd, {}).get("stdout_log")
                if log_path and os.path.exists(log_path):
                    file_paths.append(log_path)
    return file_paths
        
async def fetch_results(domain_id, manager, scan_type):
    # Ensure last_position is always initialized
    file_paths = get_file_paths(domain_id, manager, scan_type)
    
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
        
        await asyncio.sleep(1)

async def get_results(domain_id, scan_type):
    async for result in fetch_results(domain_id, manager, scan_type):
        return result

