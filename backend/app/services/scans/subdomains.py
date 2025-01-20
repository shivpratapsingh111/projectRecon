import datetime, time, subprocess
from app.config.config  import *
from backend.app.interface.process_manager import run_commands
from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='web_scan', enable_debug = True)


group_results = {}

def organise_subdomains(group_name, domain_list):

    for domain in domain_list:
        result_dir = f"{root_Data_Dir}/{group_name}/{domain}/subdomains"

        logger.debug(f"Starting to organise Subdomain Enum for {domain}")

        if os.path.exists(f"{result_dir}/{active_CombinedSubdomainResults}"):

            commands = [
                ("Organising Subdomains - 1", f"""cat {result_dir}/{passive_CombinedSubdomainResults} {result_dir}/{active_CombinedSubdomainResults} | awk '{{print $1}}' | awk '{{print tolower($0)}}' | grep -iE "^(.*\\.)?{domain}$" | sed 's/^[^a-zA-Z0-9]*//' | sed -E 's#^https?://##; s#^www*\\.##' | sort -u >> {result_dir}/{subdomainResults}""", f"{root_Data_Dir}/{group_name}/{central_log_file}", f"{root_Data_Dir}/{group_name}/{central_log_file}")
            ]

            # Execute commands and store the result
            group_results[domain] = run_commands(group_name, domain, commands, scan_dir="subdomains", execution_style="sequential")
    
            logger.debug(f"Organising Subdomains - 1 (first step) [Completed] [{domain}]")


        else:
            commands = [
                ("Organising Subdomains - 2", f"cp {result_dir}/{passive_CombinedSubdomainResults} {result_dir}/{subdomainResults}", f"{root_Data_Dir}/{group_name}/{central_log_file}", f"{root_Data_Dir}/{group_name}/{central_log_file}")
            ]

            # Execute commands and store the result
            group_results[domain] = run_commands(group_name, domain, commands, scan_dir="subdomains", execution_style="sequential")
    
            logger.debug(f"Organising Subdomains - 2 (second step) [Completed] [{domain}]")

            commands = [
                ("Organising Subdomains - 3", f"""cat {result_dir}/{subdomainResults} | awk '{{print $1}}' | awk '{{print tolower($0)}}' | grep -iE "^(.*\\.)?{domain}$" | sed 's/^[^a-zA-Z0-9]*//' | sed -E 's#^https?://##; s#^www*\\.##' | sort -u -o {result_dir}/{subdomainResults}""", f"{root_Data_Dir}/{group_name}/{central_log_file}", f"{root_Data_Dir}/{group_name}/{central_log_file}")
            ]

            # Execute commands and store the result
            group_results[domain] = run_commands(group_name, domain, commands, scan_dir="subdomains", execution_style="sequential")
    
        logger.info(f"Organising Subdomains completed - 3 (last step) [{domain}]")


def screenshot_subdomains(group_name, domain_list):
    for domain in domain_list:
        logger.debug(f"Screenshoting for {domain}")
        result_dir = f"{root_Data_Dir}/{group_name}/{domain}/subdomains/screenshots"
        os.makedirs(result_dir, exist_ok=True) # Making a directory for each domain passed as targets

        commands = [
            ("Screenshot Subdomains", f"cd {root_Data_Dir}/{group_name}/{domain}/subdomains && nuclei -l {root_Data_Dir}/{group_name}/{domain}/subdomains/{subdomainResults} -headless -t ~/nuclei-templates/headless/screenshot.yaml -c 100", f"{root_Data_Dir}/{group_name}/{central_log_file}", f"{root_Data_Dir}/{group_name}/{central_log_file}")
        ]
        # Execute commands and store the result
        group_results[domain] = run_commands(group_name, domain, commands, scan_dir="subdomains", execution_style="sequential")

    logger.info("Screenshot completed")


def func_subdomains_ps(group_name, domain_list, execution_style):

    # Store results for each domain
    group_results = {}
    
    # Execute commands for a group of domains
    for domain in domain_list:
        result_dir = f"{root_Data_Dir}/{group_name}/{domain}/subdomains"
        os.makedirs(result_dir, exist_ok=True)
        os.makedirs(f"{root_Data_Dir}/{group_name}/{domain}/subdomains/logs", exist_ok=True)
        commands = [
            ("assetfinder", f"echo {domain} | assetfinder", f"{result_dir}/{assetfinder_Passive_SubdomainResults}", f"{result_dir}/logs/{assetfinder_Passive_SubdomainResults}"),
            ("subfinder", f"echo {domain}  | subfinder", f"{result_dir}/{subfinder_Passive_SubdomainResults}", f"{result_dir}/logs/{subfinder_Passive_SubdomainResults}"),
            ("subdominator", f"subdominator -d {domain}", f"{result_dir}/{subdominator_Passive_SubdomainResults}", f"{result_dir}/logs/{subdominator_Passive_SubdomainResults}")
        ]
        
        # Execute commands and store the result
        group_results[domain] = run_commands(group_name, domain, commands, scan_dir="subdomains", execution_style=execution_style)
 

    for domain in domain_list:
        result_dir = f"{root_Data_Dir}/{group_name}/{domain}/subdomains"

        command = f"cat {result_dir}/{assetfinder_Passive_SubdomainResults} {result_dir}/{subfinder_Passive_SubdomainResults} {result_dir}/{subdominator_Passive_SubdomainResults} | sort -u >> {result_dir}/{passive_CombinedSubdomainResults}" # Combining passive results
        with open(f"{root_Data_Dir}/{group_name}/{central_log_file}" , "a") as writeLog:
            process = subprocess.Popen(
                command,
                # stdout=writeLog,
                stderr=writeLog,
                shell=True,
            )
            process.wait()
        logger.info(f"Passive Subdomains completed for {domain}")


def func_subdomains_ac(group_name, domain_list, execution_style):
    
    # Store results for each domain
    group_results = {}
    
    # Execute commands for a group of domains
    for domain in domain_list:
        result_dir = f"{root_Data_Dir}/{group_name}/{domain}/subdomains"
        os.makedirs(result_dir, exist_ok=True)
        
        # First command: alterx processing
        commands = [
            ("alterx", f"cat {result_dir}/{passive_CombinedSubdomainResults} | alterx", 
             f"{result_dir}/{alterx_Active_SubdomainResults}", 
             f"{result_dir}/logs/{alterx_Active_SubdomainResults}")
        ]
        group_results[domain] = run_commands(group_name, domain, commands, scan_dir="subdomains", execution_style=execution_style)

    # Execute DNS resolver commands
    for domain in domain_list:
        result_dir = f"{root_Data_Dir}/{group_name}/{domain}/subdomains"
        
        # Second command: DNS resolver
        commands = [
            ("dnsresolver", f"cat {result_dir}/{alterx_Active_SubdomainResults} | dnsresolver --resolvers {puredns_ResolversFile}", 
             f"{result_dir}/{active_CombinedSubdomainResults}", 
             f"{result_dir}/logs/{active_CombinedSubdomainResults}")
        ]
        group_results[f"{domain}_dnsresolver"] = run_commands(group_name, domain, commands, scan_dir="subdomains", execution_style="parallel")
    
    logger.info(f"Active Subdomains completed for {domain}")


    return group_results



def func_subdomains_both(group_name, domain_list, execution_style):
    logger.debug("Executing: func_subdomains_both")
    func_subdomains_ps(group_name, domain_list, execution_style)
    func_subdomains_ac(group_name, domain_list, execution_style)
    organise_subdomains(group_name,domain_list)
    screenshot_subdomains(group_name, domain_list)


def func_subdomains_ps_only(group_name, domain_list, execution_style):
    logger.debug("Executing: func_subdomains_ps_only")
    func_subdomains_ps(group_name, domain_list, execution_style)
    logger.debug("Passive Subdomain Enumeration completed")
    organise_subdomains(group_name,domain_list)
    screenshot_subdomains(group_name, domain_list)
