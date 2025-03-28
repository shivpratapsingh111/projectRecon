# import datetime, time, subprocess
# from app.config.config  import *
# from app.interface.process_manager import DomainCommandManager

# manager = DomainCommandManager()
# program_results = {}

# openredirectResults='openRedirects.txt' 
# ssrfResults='ssrfUrls.txt'


# def are_all_commands_completed(program_name):
#     """
#     Check if all commands in the data have status 'completed'.
#     :param data: Dictionary containing program_name, domains, and commands
#     :return: True if all commands have 'completed' status, False otherwise
#     """
#     while True:
#         data = manager.command_monitor(program_name)
#         # Loop through all domains
#         for target_uuid, domain_data in data.get('domains', {}).items():
#             commands = domain_data.get('commands', {})
#             # Loop through all commands
#             for command_name, command_data in commands.items():
#                 if command_data.get('status') != 'completed':
#                     break  # Return False immediately if any status is not 'completed'
#         return data  # Return True if all commands are 'completed'
#         time.sleep(5)

# def func_ssrf(program_name, domain_list):

#     # Store results for each domain
#     program_results = {}
    
#     # Execute commands for a program of domains
#     for domain in domain_list:
#         result_dir = f"{ROOT_DATA_DIR}/{program_name}/{domain}/ssrf"
#         os.makedirs(result_dir, exist_ok=True)
#         os.makedirs(f"{result_dir}/logs", exist_ok=True)
#         commands = [
#             ("ssrf", f"python3 backend/app/services/pyscripts/ssrf_script.py {ROOT_DATA_DIR}/{program_name}/{domain}/{urls_file} {link}", f"{result_dir}/{nucleiResults}_stdout", f"{result_dir}/logs/{nucleiResults}")
#         ]
        
#         # Execute commands and store the result
#         program_results[domain] = manager.command_executor(program_name, domain_list, domain, commands, scan_dir="subdomains")
 
#     final_monitoring_result = are_all_commands_completed(program_name)
#     print(f"SSRF Completed")