import datetime, time, subprocess
from app.config.config  import *
from app.interface.process_manager import DomainCommandManager

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

def func_xss(group_name, domain_list):

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
        group_results[domain] = manager.command_executor(group_name, domain_list, domain, commands, scan_dir="subdomains")
 
    final_monitoring_result = are_all_commands_completed(group_name)
    print(f"Xss Completed")