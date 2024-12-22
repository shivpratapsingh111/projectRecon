import datetime, time, subprocess
from app.config.config  import *
from app.interface.process_manager import DomainCommandManager

def organise_subdomains(group_name, domain_list):

    for domain in domain_list:
        result_dir = f"{root_Data_Dir}/{group_name}/{domain}/subdomains"

        print(f"Organising Subdomain Enum for {domain}")

        if os.path.exists(f"{result_dir}/{active_CombinedSubdomainResults}"):

            command = f"""cat {result_dir}/{passive_CombinedSubdomainResults} {result_dir}/{active_CombinedSubdomainResults} | awk '{{print $1}}' | awk '{{print tolower($0)}}' | grep -iE "^(.*\\.)?{domain}$" | sed 's/^[^a-zA-Z0-9]*//' | sed -E 's#^https?://##; s#^www*\\.##' | sort -u >> {result_dir}/{subdomainResults}"""
            with open(f"{root_Data_Dir}/{group_name}/{central_log_file}" , "a") as writeLog:
                process = subprocess.Popen(
                    command,
                    # stdout=writeLog,
                    stderr=writeLog,
                    shell=True,
                )
                process.wait()
        else:
            command = f"cp {result_dir}/{passive_CombinedSubdomainResults} {result_dir}/{subdomainResults}"
            with open(f"{root_Data_Dir}/{group_name}/{central_log_file}" , "a") as writeLog:
                process = subprocess.Popen(
                    command,
                    # stdout=writeLog,
                    stderr=writeLog,
                    shell=True,
                )
                process.wait()

            command = f"""cat {result_dir}/{subdomainResults} | awk '{{print $1}}' | awk '{{print tolower($0)}}' | grep -iE "^(.*\\.)?{domain}$" | sed 's/^[^a-zA-Z0-9]*//' | sed -E 's#^https?://##; s#^www*\\.##' | sort -u -o {result_dir}/{subdomainResults}"""
            with open(f"{root_Data_Dir}/{group_name}/{central_log_file}" , "a") as writeLog:
                process = subprocess.Popen(
                    command,
                    # stdout=writeLog,
                    stderr=writeLog,
                    shell=True,
                )
                process.wait()


def screenshot_subdomains(group_name, domain_list):
    for domain in domain_list:
        print(f"Screenshoting for {domain}")
        result_dir = f"{root_Data_Dir}/{group_name}/{domain}/subdomains/screenshots"
        os.makedirs(result_dir, exist_ok=True) # Making a directory for each domain passed as targets
        
        command = f"cd {root_Data_Dir}/{group_name}/{domain}/subdomains && nuclei -l {root_Data_Dir}/{group_name}/{domain}/subdomains/{subdomainResults} -headless -t ~/nuclei-templates/headless/screenshot.yaml -c 100"

        with open(f"{root_Data_Dir}/{group_name}/{central_log_file}" , "a") as writeLog:
            process = subprocess.Popen(
                command,
                # stdout=writeLog,
                stderr=writeLog,
                shell=True,
            )
            process.wait()

        print(f"Screenshot completed for {domain}")


def func_subdomains_ps(group_name, domain_list):

    manager = DomainCommandManager(log_dir=f"{root_Data_Dir}/{group_name}")


    # Store results for each domain
    group_results = {}
    
    # Execute commands for a group of domains
    for domain in domain_list:
        result_dir = f"{root_Data_Dir}/{group_name}/{domain}/subdomains"
        os.makedirs(result_dir, exist_ok=True)
        commands = [
            ("assetfinder", f"echo {domain} | assetfinder", f"{result_dir}/{assetfinder_Passive_SubdomainResults}", f"{result_dir}/logs/{assetfinder_Passive_SubdomainResults}"),
            ("subfinder", f"echo {domain}  | subfinder", f"{result_dir}/{subfinder_Passive_SubdomainResults}", f"{result_dir}/logs/{subfinder_Passive_SubdomainResults}"),
            ("subdominator", f"subdominator -d {domain}", f"{result_dir}/{subdominator_Passive_SubdomainResults}", f"{result_dir}/logs/{subdominator_Passive_SubdomainResults}")
        ]
        
        # Execute commands and store the result
        group_results[domain] = manager.command_executor(group_name, domain_list, domain, commands, scan_dir="subdomains")
 

    def are_all_commands_completed():
        """
        Check if all commands in the data have status 'completed'.

        :param data: Dictionary containing group_name, domains, and commands
        :return: True if all commands have 'completed' status, False otherwise
        """
        while True:
            data = manager.command_monitor(group_name)
            print("Waiting for the preocesses to get completed")    
            print(data)
            print("--------Values--------\n")
            print(data.values())

            # Loop through all domains
            for domain_id, domain_data in data.get('domains', {}).items():
                commands = domain_data.get('commands', {})
                # Loop through all commands
                for command_name, command_data in commands.items():
                    if command_data.get('status') != 'completed':
                        break  # Return False immediately if any status is not 'completed'
            return data  # Return True if all commands are 'completed'
            time.sleep(5)

    final_monitoring_result = are_all_commands_completed()
    print("Group Monitoring Results:", final_monitoring_result)


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
        print("Passive Subdomains combined for", domain)


def func_subdomains_ac(group_name, domain_list):
    manager = DomainCommandManager(log_dir=f"{root_Data_Dir}/{group_name}")
    
    # Store results for each domain
    group_results = {}
    
    # Execute commands for a group of domains
    for domain in domain_list:
        result_dir = f"{root_Data_Dir}/{group_name}/{domain}/subdomains"
        os.makedirs(result_dir, exist_ok=True)
        
        # First command: alterx processing
        commands = [
            (f"cat {result_dir}/{passive_CombinedSubdomainResults} | alterx", 
             f"{result_dir}/{alterx_Active_SubdomainResults}", 
             f"{result_dir}/logs/{alterx_Active_SubdomainResults}")
        ]
        group_results[f"{domain}_alterx"] = manager.command_executor(group_name, domain_list, domain, commands, scan_dir="subdomains")
    
    # Wait for all alterx processes to complete
    def wait_for_alterx_processes():
        while True:
            monitoring_result = manager.command_monitor(group_name)
            
            # Check if all alterx processes are completed
            if all('alterx' in result.get('stdout_log_file', '') and result.get('status') == 'completed' 
                   for result in monitoring_result.values()):
                return monitoring_result
            
            time.sleep(5)  # Check every 5 seconds
    
    # Wait for alterx processes
    wait_for_alterx_processes()
    
    # Execute DNS resolver commands
    for domain in domain_list:
        result_dir = f"{root_Data_Dir}/{group_name}/{domain}/subdomains"
        
        # Second command: DNS resolver
        commands = [
            (f"cat {result_dir}/{alterx_Active_SubdomainResults} | dnsresolver --resolvers {puredns_ResolversFile}", 
             f"{result_dir}/{active_CombinedSubdomainResults}", 
             f"{result_dir}/logs/{active_CombinedSubdomainResults}")
        ]
        group_results[f"{domain}_dnsresolver"] = manager.command_executor(group_name, domain_list, domain, commands, scan_dir="subdomains")
    
    # Wait for all DNS resolver processes to complete
    def wait_for_dns_processes():
        while True:
            monitoring_result = manager.command_monitor(group_name)
            
            # Check if all DNS resolver processes are completed
            if all('dnsresolver' in str(result.get('stdout_log_file', '')).lower() and result.get('status') == 'completed' 
                   for result in monitoring_result.values()):
                return monitoring_result
            
            time.sleep(5)  # Check every 5 seconds
    
    # Get final monitoring results for DNS resolver processes
    final_monitoring_result = wait_for_dns_processes()
    print("Group Monitoring Results:", final_monitoring_result)
    
    return group_results



def func_subdomains_both(group_name, domain_list):
    print("Executing: func_subdomains_both")
    func_subdomains_ps(group_name, domain_list)
    func_subdomains_ac(group_name, domain_list)
    organise_subdomains(group_name,domain_list)
    screenshot_subdomains(group_name, domain_list)


def func_subdomains_ps_only(group_name, domain_list):
    print("Executing: func_subdomains_ps_only")
    func_subdomains_ps(group_name, domain_list)
    organise_subdomains(group_name,domain_list)
    screenshot_subdomains(group_name, domain_list)
