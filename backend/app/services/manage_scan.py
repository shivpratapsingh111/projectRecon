from concurrent.futures import ThreadPoolExecutor
from app.config.config  import *
from app.services.pyscripts.urls import func_urls_both
from app.services.pyscripts.subdomains import func_subdomains_both
from app.services.pyscripts.subdomains import func_subdomains_ps_only
import os
# from app.config.celery_config import celery

# def func_js(group_name, domain_list):
#     result_dir = f"{target_dir}js"
#     os.makedirs(result_dir, exist_ok=True) # Making subdomains/ directory inside target directory
#     print("Executing: func_js")

# def func_nuclei(group_name, domain_list):
#     result_dir = f"{target_dir}nuclei"
#     os.makedirs(result_dir, exist_ok=True) # Making subdomains/ directory inside target directory
#     print("Executing: func_nuclei")

# def func_nmap(group_name, domain_list):
#     result_dir = f"{target_dir}nmap"
#     os.makedirs(result_dir, exist_ok=True) # Making subdomains/ directory inside target directory
#     print("Executing: func_nmap")

# @celery.task
def start_scan(group_name, domain_list, scan_list):
    global root_Data_Dir  # Define root directory
    
    # Define target directory and logs
    target_dir = f"{root_Data_Dir}/{group_name}"
    os.makedirs(target_dir, exist_ok=True)  # Create main target directory and logs directory
    
    targets_file = f"{target_dir}/targets.txt"
    
    # Write domain list to file
    with open(targets_file, 'w') as f:
        for domain in domain_list:
            f.write(domain.strip() + "\n")
    
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
                    return {"error": f"'{related_scan}' requires '{scan}' to be executed first."}
            # Execute the scan
            actions[scan](group_name, domain_list)
            completed_scans.add(scan)
    
    # Step 2: Execute remaining scans in any order
    for scan in scan_list:
        if scan not in completed_scans:  # Skip already executed scans
            if scan in actions:
                actions[scan](group_name, domain_list)  # Execute the scan
                completed_scans.add(scan)
            else:
                return {"error": f"Invalid scan: '{scan}'."}
    
    return {"status": "All scans executed successfully", "executed_scans": list(completed_scans)}
    


# scan_list = ["subdomains_ps_only"]
# domain_list = ["thecyberboy.com"]
# group_name = "heavy"
# start_scan(group_name, domain_list, scan_list)