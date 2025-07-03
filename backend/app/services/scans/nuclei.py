# External imports
import os

# Internal imports
from app.interface.process_manager import run_commands
from app.interface.logger_manager import setup_logger
from app.config.config import (
	ROOT_DATA_DIR,
    LOG_LEVEL_DEBUG,
    nuclei_file,
    subdomains_file,
)

# Initialization
logger = setup_logger(__name__, log_file_path='service', enable_debug = LOG_LEVEL_DEBUG)
program_results = {}

# Logic
# DO NOT REMOVE PARAMETER: `execution_style`
def start_nuclei_scan(program_name, domain_list, execution_style, nuclei_enum, program_uuid, target_uuid_list):
    # Store results for each domain
    program_results = {}
    
    # Execute commands for a program of domains
    for domain, target_uuid in zip(domain_list, target_uuid_list):
        result_dir = f"{ROOT_DATA_DIR}/{program_name}/{domain}/nuclei"
        os.makedirs(result_dir, exist_ok=True)
        os.makedirs(f"{result_dir}/.logs", exist_ok=True)
        commands = [
            (
                "nuclei",
                f"nuclei -l {ROOT_DATA_DIR}/{program_name}/{domain}/subdomains/{subdomains_file} -t ~/nuclei-templates/ -o {result_dir}/{nuclei_file}",
                f"{result_dir}/.logs/{nuclei_file.removesuffix('.txt')}_stdout",
                f"{result_dir}/.logs/{nuclei_file.removesuffix('.txt')}_stderr"
            )
        ]
        program_results[domain] = run_commands(program_name, domain, commands, program_uuid, target_uuid, scan_dir="nuclei", execution_style="sequential")
 
        logger.info(f"[SCAN - NUCLEI] COMPLETED [{program_name} - {domain}]")
    logger.info(f"[SCAN - NUCLEI] COMPLETED [{program_name}]")

