import datetime, time, subprocess
from app.config.config  import *
from app.interface.process_manager import run_commands
from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='web_scan', enable_debug = True)

group_results = {}

def func_nuclei_run(group_name, domain_list):

    # Store results for each domain
    group_results = {}
    
    # Execute commands for a group of domains
    for domain in domain_list:
        result_dir = f"{root_Data_Dir}/{group_name}/{domain}/nuclei"
        os.makedirs(result_dir, exist_ok=True)
        os.makedirs(f"{result_dir}/logs", exist_ok=True)
        commands = [
            ("nuclei", f"nuclei -l {root_Data_Dir}/{group_name}/{domain}/subdomains/{subdomainResults} -t ~/nuclei-templates/ -c 50 -fr -rl 20 -timeout 20 -o {result_dir}/{nucleiResults}", f"{result_dir}/{nucleiResults}_stdout", f"{result_dir}/logs/{nucleiResults}")
        ]
        
        # Execute commands and store the result
        group_results[domain] = run_commands(group_name, domain, commands, scan_dir="nuclei", execution_style="sequential")
 
    logger.info(f"Nuclei scan completed")
    

# DO NOT REMOVE PARAMETER: `execution_style`
def func_nuclei(group_name, domain_list, execution_style):
    func_nuclei_run(group_name, domain_list)