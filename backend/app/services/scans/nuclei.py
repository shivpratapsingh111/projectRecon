import datetime, time, subprocess
from app.config.config  import *
from app.interface.process_manager import run_commands
from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='web_scan', enable_debug = True)

group_results = {}

# DO NOT REMOVE PARAMETER: `execution_style`
def start_nuclei_scan(group_name, domain_list, execution_style, nuclei_enum):
    # Store results for each domain
    group_results = {}
    
    # Execute commands for a group of domains
    for domain in domain_list:
        result_dir = f"{ROOT_DATA_DIR}/{group_name}/{domain}/nuclei"
        os.makedirs(result_dir, exist_ok=True)
        os.makedirs(f"{result_dir}/logs", exist_ok=True)
        commands = [
            (
                "nuclei",
                f"nuclei -l {ROOT_DATA_DIR}/{group_name}/{domain}/subdomains/{subdomains_file} -t ~/nuclei-templates/ -o {result_dir}/{nuclei_file}",
                f"{result_dir}/{nuclei_file}_stdout",
                f"{result_dir}/logs/{nuclei_file}"
            )
        ]
        
        # Execute commands and store the result
        group_results[domain] = run_commands(group_name, domain, commands, scan_dir="nuclei", execution_style="sequential")
 
    logger.info(f"Nuclei scan completed")
