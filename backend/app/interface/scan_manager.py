from concurrent.futures import ThreadPoolExecutor
from app.config.config  import *
from app.services.scans.urls import start_urls_scan
from app.services.scans.subdomains import start_subdomains_scan
from app.services.scans.nuclei import start_nuclei_scan
from app.services.scans.js import start_js_scan
import os
from app.logger.logger import setup_logger
from app.interface.json_data_manager import GroupManager
from app.config.db_config  import db_config
from app.db.db_operations import DatabaseOperations
from app.db.db_manager import DatabaseManager
db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)

group_manager = GroupManager()
logger = setup_logger(__name__, log_file_path='web_scan', enable_debug = True)


def start_scan(group_name, domain_list, execution_style, scan_config):
    """
        - Make scan directory
        - Write provided targets to targets.txt
        - Call run_scans
    """
    target_dir = f"{ROOT_DATA_DIR}/{group_name}"
    os.makedirs(target_dir, exist_ok=True)
    logger.debug(f"Made target dir {target_dir}")
    targets_file = f"{target_dir}/targets.txt"
    
    existing_domains = set()
    if os.path.exists(targets_file):
        with open(targets_file, 'r') as f:
            existing_domains = set(line.strip() for line in f.readlines())
    
    existing_domains.update(domain.strip() for domain in domain_list)
    
    with open(targets_file, 'a') as f:
        for domain in sorted(existing_domains):
            f.write(domain + "\n")
            
    logger.debug(f"Written domains to file: {targets_file}")

    run_scans(group_name, domain_list, execution_style, scan_config)

def check_and_insert_program_and_target(group_name, domain_list):
    
    program_data = {
    "program_name": group_name,
    "program_url": None,
    "acquisitions": [""],
    "email": None,
    "report_form": None
    }
    domain_id_list= []
    exists = db_ops.query_operations().check_program_exists(group_name)
    if exists:
        program_id = db_ops.query_operations().get_program_id(group_name)
        logger.debug(f"Program exists [{group_name}]-[{program_id}]")
    else:
        program_id = db_ops.insert_operations().insert_program(program_data)
        logger.debug(f"New program [{group_name}] created with id {program_id}")
    
    for domain in domain_list:
        exists = db_ops.query_operations().check_web_target_exists(domain)
        if exists:
            domain_id = db_ops.query_operations().get_web_target_id(domain)
            logger.debug(f"Domain [{domain}] exists in DB [{domain_id}]")
            domain_id_list.append(domain_id)
        else:
            domain_id = db_ops.insert_operations().insert_web_target_new(program_id, domain)
            domain_id_list.append(domain_id)
            logger.debug(f"New Domain [{domain}] inserted in DB with id {domain_id}")
    
    logger.debug(f"All Targets inserted in DB with IDs {domain_id_list}")
    return program_id, domain_id_list

def run_scans(group_name, domain_list, execution_style, scan_config):
    """
        - Call respective scan functions to start scans provided in scan_config
    """

    completed_scans = set()
    
    subdomain_enum = scan_config.get("subdomainEnum", {})
    url_enum = scan_config.get("urlEnum", {})
    nuclei_enum = scan_config.get("nuclei", {})
    nmap_enum = scan_config.get("nmap", {})
    js_enum = scan_config.get("js", {})

    program_id, domain_id_list = check_and_insert_program_and_target(group_name, domain_list)    

    if not subdomain_enum.get("run", False):
        logger.info("Subdomain enumeration is disabled.")
    else:
        start_subdomains_scan(group_name, domain_list, execution_style, subdomain_enum, program_id, domain_id_list)
        completed_scans.add("Subdomain Enumeration")

    if not url_enum.get("run", False):
        logger.info("url_enum is disabled.")
    else:
        start_urls_scan(group_name, domain_list, execution_style, url_enum, program_id, domain_id_list)
        completed_scans.add("URL Enumeration")

    if not nuclei_enum.get("run", False):
        logger.info("nuclei is disabled.")
    else:
        start_nuclei_scan(group_name, domain_list, execution_style, nuclei_enum, program_id, domain_id_list)
        completed_scans.add("Nuclei")

    if not js_enum.get("run", False):
        logger.info("js is disabled.")
    else:
        start_js_scan(group_name, domain_list, execution_style, js_enum, program_id, domain_id_list)
        # logger.warning("js is not configured yet.")
        completed_scans.add("JS")

    if not nmap_enum.get("run", False):
        logger.info("nmap is disabled.")
    else:
        logger.warning("nmap is not configured yet.")
        completed_scans.add("Nmap")

    logger.info(f"Scans executed successfully {list(completed_scans)}")

# run_scans(group_name="group-1", domain_list=['thecyberboy.com'], execution_style="parallel", scan_config=config)