from concurrent.futures import ThreadPoolExecutor
from app.config.config  import *
from backend.app.services.scans.urls import func_urls_both
from backend.app.services.scans.subdomains import func_subdomains_both
from backend.app.services.scans.subdomains import func_subdomains_ps_only
import os
from app.services.monitor_endpoints.db.db_manager import DatabaseManager
from app.services.monitor_endpoints.db.db_operations import DatabaseOperations
from app.logger.logger import setup_logger
from app.config.db_config import db_config
logger = setup_logger(__name__, log_file_path='web_scan', enable_debug = True)


db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)

# from app.config.celery_config import celery

# def func_js(group_name, domain_list, execution_style):
#     result_dir = f"{target_dir}js"
#     os.makedirs(result_dir, exist_ok=True) # Making subdomains/ directory inside target directory
#     print("Executing: func_js")

# def func_nuclei(group_name, domain_list, execution_style):
#     result_dir = f"{target_dir}nuclei"
#     os.makedirs(result_dir, exist_ok=True) # Making subdomains/ directory inside target directory
#     print("Executing: func_nuclei")

# def func_nmap(group_name, domain_list, execution_style):
#     result_dir = f"{target_dir}nmap"
#     os.makedirs(result_dir, exist_ok=True) # Making subdomains/ directory inside target directory
#     print("Executing: func_nmap")

# @celery.task
def start_scan(group_name, domain_list, execution_style, scan_list):
    global root_Data_Dir  # Define root directory
    
    # Define target directory and logs
    target_dir = f"{root_Data_Dir}/{group_name}"
    os.makedirs(target_dir, exist_ok=True)  # Create main target directory and logs directory
    logger.debug(f"Made target dir {target_dir}")
    targets_file = f"{target_dir}/targets.txt"
    
    # Write domain list to file
    # with open(targets_file, 'a') as f:
    #     for domain in domain_list:
    #         f.write(domain.strip() + "\n")

    existing_domains = set()
    if os.path.exists(targets_file):
        with open(targets_file, 'r') as f:
            existing_domains = set(line.strip() for line in f.readlines())
    # Add new domains to the set
    existing_domains.update(domain.strip() for domain in domain_list)
    # Write the unique domains back to the file
    with open(targets_file, 'a') as f:
        for domain in sorted(existing_domains):  # Sorting if desired, otherwise remove `sorted`
            f.write(domain + "\n")
            
    logger.debug(f"Written domains to file: {targets_file}")
    # Define the actions and their respective functions
    actions = {
        "subdomainBoth": func_subdomains_both,
        "subdomainPassive": func_subdomains_ps_only,
        "urlsBoth": func_urls_both,
        # "subdomains_ac_only": func_subdomains_ac_only,
        # "urls_ps_only": func_urls_ps_only,
        # "urls_ac_only": func_urls_ac_only,
        # "xss": func_xss,
        # "js": func_js,
        # "nuclei": func_nuclei,
        # "nmap": func_nmap,
    }
    
    # Enforced order of execution for related scans
    required_order = {
        "subdomains_both": ["subdomains_ps_only", "subdomains_ac_only"],
        "urls_both": ["urls_ps_only", "urls_ac_only"],
    }
    
    # Validate input scan_list
    completed_scans = set()
    
    # Step 1: Ensure mandatory scans are executed in order
    for scan in required_order:
        if scan in scan_list:
            # Ensure that the related scans are executed in order
            related_scans = required_order[scan]
            for related_scan in related_scans:
                if related_scan in scan_list and related_scan not in completed_scans:
                    logger.error(f"'{related_scan}' requires '{scan}' to be executed first.")
                    return {"error": f"'{related_scan}' requires '{scan}' to be executed first."}
            # Execute the scan
            logger.debug(f"Calling {scan}({group_name, domain_list, execution_style})")
            actions[scan](group_name, domain_list, execution_style)
            completed_scans.add(scan)
            logger.debug(f"Scan completed {scan}")
    
    # Step 2: Execute remaining scans in any order
    for scan in scan_list:
        if scan not in completed_scans:  # Skip already executed scans
            # logger.debug(f"Scan {scan} is aready completed")
            if scan in actions:
                logger.debug(f"Calling {scan}({group_name, domain_list, execution_style})")
                actions[scan](group_name, domain_list, execution_style)  # Execute the scan
                completed_scans.add(scan)
                logger.debug(f"Scan completed {scan}")
            else:
                logger.error(f"Invalid Scan {scan}")
                return {"error": f"Invalid scan: '{scan}'."}
    logger.info("All scans executed successfully")
    return {"status": "All scans executed successfully", "executed_scans": list(completed_scans)}
    


# scan_list = ["subdomains_ps_only"]
# domain_list = ["thecyberboy.com"]
# group_name = "heavy"
# start_scan(group_name, domain_list, execution_style, scan_list)