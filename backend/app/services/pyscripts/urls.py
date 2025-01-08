from app.config.config  import *
import os, re, requests, subprocess, datetime, time
from app.interface.process_manager import DomainCommandManager
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.services.pyscripts.arrange_urls import arrangeUrls
manager = DomainCommandManager()
group_results = {}

def are_all_commands_completed(group_name):
    """
    Check if all commands in the data have status 'completed'.
    :param data: Dictionary containing group_name, domains, and commands
    :return: True if all commands have 'completed' status, False otherwise
    """
    while True:
        data = manager.command_monitor(group_name)
        # Loop through all domains
        for domain_id, domain_data in data.get('domains', {}).items():
            commands = domain_data.get('commands', {})
            # Loop through all commands
            for command_name, command_data in commands.items():
                if command_data.get('status') != 'completed':
                    break  # Return False immediately if any status is not 'completed'
        return data  # Return True if all commands are 'completed'
        time.sleep(5)

def func_urls_ps(group_name, domain_list):
    print("Executing: func_urls_ps")

    # Store results for each domain
    group_results = {}
    
    # Execute commands for a group of domains
    for domain in domain_list:
        result_dir = f"{root_Data_Dir}/{group_name}/{domain}/urls"
        domain_dir = f"{root_Data_Dir}/{group_name}/{domain}"
        os.makedirs(result_dir, exist_ok=True)
        os.makedirs(f"{root_Data_Dir}/{group_name}/{domain}/urls/logs", exist_ok=True)
        commands = [
            ("waybackurls", f"cat {domain_dir}/subdomains/{subdomainResults} | waybackurls", f"{result_dir}/{waybackurls_Passive_UrlResults}", f"{result_dir}/logs/{waybackurls_Passive_UrlResults}"),
            ("gau", f"cat {domain_dir}/subdomains/{subdomainResults} | gau", f"{result_dir}/{gau_Passive_UrlResults}", f"{result_dir}/logs/{gau_Passive_UrlResults}"),
            ("waymore", f"waymore -n -xwm -urlr 0 -r 2 -i {domain} -mode U -oU {result_dir}/{waymore_Passive_UrlResults}", f"{result_dir}/{waymore_Passive_UrlResults}_stdout", f"{result_dir}/logs/{waymore_Passive_UrlResults}")
        ]
        
        # Execute commands and store the result
        group_results[domain] = manager.command_executor(group_name, domain_list, domain, commands, scan_dir="urls")

    final_monitoring_result = are_all_commands_completed(group_name)

    for domain in domain_list:
        command = f"cat {result_dir}/{waybackurls_Passive_UrlResults} {result_dir}/{gau_Passive_UrlResults} {result_dir}/{waymore_Passive_UrlResults} | sort -u >> {result_dir}/{passive_CombinedUrlResults}" # Combining passive results
        with open(f"{root_Data_Dir}/{group_name}/{central_log_file}" , "a") as writeLog:
            process = subprocess.Popen(
                command,
                # stdout=writeLog,
                stderr=writeLog,
                shell=True,
            )
            process.wait()

        print(f"Passive URL Enum completed")


def func_urls_ac(group_name, domain_list):
    print("Executing: func_urls_ac")

    # Store results for each domain
    group_results = {}
    
    # Execute commands for a group of domains
    for domain in domain_list:
        result_dir = f"{root_Data_Dir}/{group_name}/{domain}/urls"
        domain_dir = f"{root_Data_Dir}/{group_name}/{domain}"
        os.makedirs(result_dir, exist_ok=True)
        commands = [
            ("katana", f"katana -u {domain_dir}/subdomains/{subdomainResults} -o {result_dir}/{katana_Active_UrlResults} -silent -hl -nc -d 5 -aff -retry 2 -iqp -c 20 -p 20 -xhr -jc -kf -ef css,jpg,jpeg,png,svg,img,gif,mp4,flv,ogv,webm,webp,mov,mp3,m4a,m4p,scss,tif,tiff,ttf,otf,woff,woff2,bmp,ico,eot,htc,rtf,swf,image", f"{result_dir}/{katana_Active_UrlResults}_stdout", f"{result_dir}/logs/katana2from_start_tool_func"),
            ("hakrawler", f"cat {domain_dir}/subdomains/{subdomainResults} | sed 's/^/https:\/\//' | hakrawler -d 5 -insecure -subs -t 40", f"{result_dir}/{hakrawler_Active_UrlResults}", f"{result_dir}/logs/{hakrawler_Active_UrlResults}")
        ]
        
        # Execute commands and store the result
        group_results[domain] = manager.command_executor(group_name, domain_list, domain, commands, scan_dir="urls")

    final_monitoring_result = are_all_commands_completed(group_name)

    for domain in domain_list:
        command = f"cat {result_dir}/{katana_Active_UrlResults} {result_dir}/{hakrawler_Active_UrlResults} | sort -u >> {result_dir}/{active_CombinedUrlResults}" # Combining passive results
        with open(f"{root_Data_Dir}/{group_name}/{central_log_file}" , "a") as writeLog:
            process = subprocess.Popen(
                command,
                # stdout=writeLog,
                stderr=writeLog,
                shell=True,
            )
            process.wait()
        print(f"Active URL Enum completed")


def organise_urls(group_name,domain_list):
    for domain in domain_list:
        print(f"Organising URL Enum for {domain}")
        result_dir = f"{root_Data_Dir}/{group_name}/{domain}/urls"

        commands = [
            ("Organising Urls", f"cat {result_dir}/{passive_CombinedUrlResults} {result_dir}/{active_CombinedUrlResults} | sort -u >> {result_dir}/{urlResults}", f"{root_Data_Dir}/{group_name}/{central_log_file}", f"{root_Data_Dir}/{group_name}/{central_log_file}")
        ]
        # Execute commands and store the result
        group_results[domain] = manager.command_executor(group_name, domain_list, domain, commands, scan_dir="subdomains")
        final_monitoring_result = are_all_commands_completed(group_name)

        commands = [
            ("Extracting JS Urls", f"""cat {result_dir}/{urlResults} | grep -F .js | cut -d "?" -f 1 | sort -u >> {result_dir}/{jsUrls}""", f"{root_Data_Dir}/{group_name}/{central_log_file}", f"{root_Data_Dir}/{group_name}/{central_log_file}")
        ]
        # Execute commands and store the result
        group_results[domain] = manager.command_executor(group_name, domain_list, domain, commands, scan_dir="subdomains")
        final_monitoring_result = are_all_commands_completed(group_name)

        commands = [
            ("Arranging Urls", f"python3 backend/app/services/pyscripts/arrange_urls.py {result_dir}/{urlResults} {result_dir}/{urlsArranged200} {result_dir}/{urlsArrangedAll}", f"{root_Data_Dir}/{group_name}/urlsArrange_stdout", f"{root_Data_Dir}/{group_name}/{central_log_file}")
        ]
        # Execute commands and store the result
        group_results[domain] = manager.command_executor(group_name, domain_list, domain, commands, scan_dir="subdomains")
        final_monitoring_result = are_all_commands_completed(group_name)

        print(f"Urls arranged successfully for {domain}")



def func_urls_both(group_name, domain_list):
    func_urls_ps(group_name, domain_list)
    func_urls_ac(group_name, domain_list)
    organise_urls(group_name,domain_list)