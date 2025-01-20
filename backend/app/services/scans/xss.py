import datetime, time, subprocess
from app.config.config  import *
from backend.app.interface.process_manager import run_commands
from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='web_scan', enable_debug = True)

group_results = {}

def func_xss_run(group_name, domain_list):

    # Store results for each domain
    group_results = {}
    
    # Execute commands for a group of domains
    for domain in domain_list:
        result_dir = f"{root_Data_Dir}/{group_name}/{domain}/xss"
        os.makedirs(result_dir, exist_ok=True)
        os.makedirs(f"{result_dir}/logs", exist_ok=True)
        commands = [
            ("xss", f"""cat {root_Data_Dir}/{group_name}/{domain}/{urlResults} | grep = | kxss | grep '>\|<\|"'""", f"{result_dir}/{xssResults}", f"{result_dir}/logs/{xssResults}")
        ]
        
        # Execute commands and store the result
        group_results[domain] = run_commands(group_name, domain, commands, scan_dir="xss", execution_style="sequential")
 
    logger.info(f"Xss scan completed")
    

# DO NOT REMOVE PARAMETER: `execution_style`
def func_xss(group_name, domain_list, execution_style):
    func_xss_run(group_name, domain_list)