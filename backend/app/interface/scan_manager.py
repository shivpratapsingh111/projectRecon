from concurrent.futures import ThreadPoolExecutor
from app.config.config  import *
from app.services.scans.urls import start_urls_scan
from app.services.scans.subdomains import start_subdomains_scan
from app.services.scans.nuclei import start_nuclei_scan
import os
from app.logger.logger import setup_logger
from app.config.db_config import db_config

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
    
    if not subdomain_enum.get("run", False):
        logger.info("Subdomain enumeration is disabled.")
    else:
        start_subdomains_scan(group_name, domain_list, execution_style, subdomain_enum)
        completed_scans.add("Subdomain Enumeration")

    if not url_enum.get("run", False):
        logger.info("url_enum is disabled.")
    else:
        start_urls_scan(group_name, domain_list, execution_style, url_enum)
        completed_scans.add("URL Enumeration")

    if not nuclei_enum.get("run", False):
        logger.info("nuclei is disabled.")
    else:
        start_nuclei_scan(group_name, domain_list, execution_style, nuclei_enum)
        completed_scans.add("Nuclei")

    if not nmap_enum.get("run", False):
        logger.info("nmap is disabled.")
    else:
        logger.warning("nmap is not configured yet.")
        completed_scans.add("Nmap")

    if not js_enum.get("run", False):
        logger.info("js is disabled.")
    else:
        logger.warning("js is not configured yet.")
        completed_scans.add("JS")

    logger.info(f"Scans executed successfully [{list(completed_scans)}]")

# run_scans(group_name="group-1", domain_list=['thecyberboy.com'], execution_style="parallel", scan_config=config)