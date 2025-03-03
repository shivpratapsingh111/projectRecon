import datetime, time, subprocess
from app.config.config  import *
from app.interface.process_manager import run_commands
from app.logger.logger import setup_logger
from app.db.db_manager import DatabaseManager
from app.db.db_operations import DatabaseOperations
from app.config.db_config  import db_config
db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)

logger = setup_logger(__name__, log_file_path='web_scan', enable_debug = True)

group_results = {}

# DO NOT REMOVE PARAMETER: `execution_style`
def start_nuclei_scan(group_name, domain_list, execution_style, nuclei_enum, program_id, domain_id_list):
    # Store results for each domain
    group_results = {}
    
    # Execute commands for a group of domains
    for domain, domain_id in zip(domain_list, domain_id_list):
        result_dir = f"{ROOT_DATA_DIR}/{group_name}/{domain}/nuclei"
        os.makedirs(result_dir, exist_ok=True)
        os.makedirs(f"{result_dir}/.logs", exist_ok=True)
        commands = [
            (
                "nuclei",
                f"nuclei -l {ROOT_DATA_DIR}/{group_name}/{domain}/subdomains/{subdomains_file} -t ~/nuclei-templates/ -o {result_dir}/{nuclei_file}",
                f"{result_dir}/.logs/{nuclei_file.removesuffix('.txt')}_stdout",
                f"{result_dir}/.logs/{nuclei_file.removesuffix('.txt')}_stderr"
            )
        ]
        group_results[domain] = run_commands(group_name, domain, commands, program_id, domain_id, scan_dir="nuclei", execution_style="sequential")
 
        logger.info(f"[SCAN - NUCLEI] COMPLETED [{group_name} - {domain}]")
    logger.info(f"[SCAN - NUCLEI] COMPLETED [{group_name}]")

