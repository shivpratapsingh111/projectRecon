# process_manager.py

import os
import json
import threading
import multiprocessing
import psutil
import uuid
import time
import logging
import time
from datetime import datetime
import subprocess
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.config.config  import *
# from app.test.data_manager import *

from datetime import datetime
from app.interface.data_manager import GroupManager

# Get current date and time
current_datetime = datetime.now()

# Format current day, date, and time
formatted_day = current_datetime.strftime("%A")          # Full day name (e.g., Monday)
formatted_date = current_datetime.strftime("%d-%m-%Y")   # Date in ISO format: YYYY-MM-DD
formatted_time = current_datetime.strftime("%H:%M:%S")   # Time in 24-hour format: HH:MM:SS

time_day_date = f"{formatted_time}, {formatted_day}, {formatted_date}"

data_manager_obj = GroupManager(data_file)

def run_command_wrapper(cmd, stdout_log_file, stderr_log_file, domain, command_name, result_queue):
    """
    Enhanced command wrapper that captures process completion and exit status
    """
    try:
        with open(stdout_log_file, 'a') as stdout_log, \
             open(stderr_log_file, 'a') as stderr_log:
            print(f"{command_name} started for: {domain}")
            process = subprocess.Popen(
                cmd, 
                shell=True, 
                stdout=stdout_log, 
                stderr=stderr_log,
                start_new_session=True
            )
            
            # Wait for the process to complete and get return code
            return_code = process.wait()
            
            # Put result in queue for parent process to retrieve
            result_queue.put({
                'domain': domain,
                'command_name': command_name,  # Add command_name here
                'pid': process.pid,
                'return_code': return_code,
                'status': 'completed' if return_code == 0 else 'failed'
            })
    except Exception as e:
        logging.error(f"Error executing command for {domain}: {e}")
        result_queue.put({
            'domain': domain,
            'command_name': command_name,  # Add command_name here
            'status': 'error',
            'error': str(e)
        })

class DomainCommandManager():
    def __init__(self, log_dir: str = 'logs'):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Setup logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'main.log')),
                logging.StreamHandler()
            ]
        )


    def initialize_data_structure(self, group_name, domain, commands):
        """
        Initialize the data structure for a new group and domain
        
        Args:
            group_name (str): Name of the group
            domain (str): Domain name
            commands (List[tuple]): List of commands to initialize
        
        Returns:
            Dict: Initialized data structure
        """
        try:
            # Generate UUIDs for group and domain
            group_uuid = str(uuid.uuid4())
            domain_uuid = str(uuid.uuid4())
            
            # Prepare the initial data structure
            initial_data = {
                "groups": {
                    group_uuid: {
                        "group_name": group_name,
                        "domains": {
                            domain_uuid: {
                                "domain_name": domain,
                                "commands": {}
                            }
                        }
                    }
                }
            }
            
            # Populate commands
            for command_name, cmd, stdout_log_file, stderr_log_file in commands:
                initial_data["groups"][group_uuid]["domains"][domain_uuid]["commands"][command_name] = {
                    "command_name": command_name,
                    "pid": None,  # Will be updated when process starts
                    "command": cmd,
                    "status": "pending",
                    "start_time": time_day_date  # Using the globally defined time_day_date
                }
            
            # Save the initial data
            data_manager_obj.write_to_file(initial_data)
            
            # Return the UUIDs for further reference
            return {
                "group_uuid": group_uuid,
                "domain_uuid": domain_uuid
            }
        
        except Exception as e:
            logging.error(f"Error initializing data structure: {e}")
            raise



    def command_executor(self, group_name: str, domain_list: List[str], domain: str, commands: List[tuple], scan_dir: str) -> Dict[str, Any]:

        try:
            # Try to load existing data
            data = data_manager_obj._read_file()
            
            # Check if group exists
            group_uuid = data_manager_obj.get_group_uuid_by_name(group_name)
            
            # If group doesn't exist, initialize
            if not group_uuid:
                initialization = self.initialize_data_structure(group_name, domain, commands)
                group_uuid = initialization["group_uuid"]
        
        except FileNotFoundError:
            # If file doesn't exist, initialize data structure
            initialization = self.initialize_data_structure(group_name, domain, commands)
            group_uuid = initialization["group_uuid"]
        except Exception as e:
            logging.error(f"Unexpected error checking data structure: {e}")
            raise

        # Create a queue to capture process results
        result_queue = multiprocessing.Queue()
        
        # Prepare command execution
        def domain_command_set(domain):
            domain_results = []
            result_dir = f"{root_Data_Dir}/{group_name}/{domain}/{scan_dir}"
            os.makedirs(result_dir, exist_ok=True)
            os.makedirs(f"{result_dir}/logs", exist_ok=True)

            processes = []
            for idx, (command_name, cmd, stdout_log_file, stderr_log_file) in enumerate(commands, 1):
                process = multiprocessing.Process(
                    target=run_command_wrapper, 
                    args=(cmd, stdout_log_file, stderr_log_file, domain, command_name, result_queue)
                )
                process.start()
                processes.append((process, command_name, cmd))

            # Wait for all processes to complete
            for process, command_name, cmd in processes:
                process.join()

            return domain_results

        # Execute commands
        with ThreadPoolExecutor(max_workers=len(domain_list)) as executor:
            future_to_domain = {
                executor.submit(domain_command_set, domain): domain 
                for domain in domain_list
            }
            
            # Process results
            execution_results = {}
            for future in as_completed(future_to_domain):
                domain = future_to_domain[future]
                try:
                    execution_results[domain] = future.result()
                except Exception as e:
                    logging.error(f"Error processing {domain}: {e}")

        # Collect and process queue results
        queue_results = []
        while not result_queue.empty():
            queue_results.append(result_queue.get())

        # Update command status in data manager
        for result in queue_results:
            self._update_command_status(result, group_name)

        return {
            'group_uuid': group_uuid,
            'execution_results': execution_results,
            'process_results': queue_results
        }


    def _update_command_status(self, result, group_name):
        """
        Update the status of a command in the data manager
        
        Args:
            result (dict): A dictionary containing process execution results
            group_name (str): Name of the group
        """
        try:
            # Retrieve the group UUID first
            group_uuid = data_manager_obj.get_group_uuid_by_name(group_name)
            
            if not group_uuid:
                logging.error(f"Could not find group UUID for {group_name}")
                return
            
            # Load the entire data
            data = data_manager_obj._read_file()
            
            # Debugging: Print out the entire groups structure
            logging.debug(f"Groups data: {json.dumps(data['groups'], indent=2)}")
            
            # Find the domain and update its command status
            domain_found = False
            for domain_uuid, domain_info in data['groups'][group_uuid]['domains'].items():
                if domain_info['domain_name'] == result['domain']:
                    # Check if the command exists in this domain
                    if result['command_name'] in domain_info['commands']:
                        # Update the specific command status
                        domain_info['commands'][result['command_name']].update({
                            "status": result.get('status', 'unknown'),
                            "pid": result.get('pid'),
                            "return_code": result.get('return_code')
                        })
                        domain_found = True
                        break
            
            if not domain_found:
                logging.error(f"Could not find domain {result['domain']} or command {result['command_name']}")
                # Optional: Print more detailed debugging information
                logging.error(f"Full result: {result}")
                logging.error(f"Group UUID: {group_uuid}")
                
                # If you want to see the exact structure
                for domain_uuid, domain_info in data['groups'][group_uuid]['domains'].items():
                    logging.error(f"Domain UUID: {domain_uuid}")
                    logging.error(f"Domain Name: {domain_info['domain_name']}")
                    logging.error(f"Commands: {list(domain_info['commands'].keys())}")
                
                return
            
            # Save the updated data
            data_manager_obj.write_to_file(data)
            
            logging.info(f"Updated status for {result['command_name']} on {result['domain']}: {result.get('status', 'unknown')}")
        
        except Exception as e:
            logging.error(f"Error updating command status: {e}")
            logging.error(f"Result details: {result}")
            import traceback
            traceback.print_exc()



    def command_monitor(self, group_name: Optional[str] = None) -> Dict:
        """
        Monitor command statuses
        """
        group_uuid = data_manager_obj.get_group_uuid_by_name(group_name)
        return data_manager_obj.get_group_by_uuid(group_uuid)   

    
    def stop_processes(self, group_name: Optional[str] = None, domain_name: Optional[str] = None):
        """
        Stop processes for a given group or domain
        
        Args:
            group_name (Optional[str]): Name of the group to stop processes for
            domain_name (Optional[str]): Name of the domain to stop processes for
        
        Returns:
            Dict: Summary of stopped processes
        """
        if not group_name and not domain_name:
            logging.error("Must provide either group_name or domain_name")
            return {"status": "error", "message": "No group or domain specified"}

        try:
            # Load the current data
            data = data_manager_obj._read_file()
            
            # Track stopped processes
            stopped_processes = []
            not_found_processes = []

            # Iterate through groups
            for group_uuid, group_data in data['groups'].items():
                # Check if group matches or if no specific group was given
                if group_name is None or group_data['group_name'] == group_name:
                    for domain_uuid, domain_data in group_data['domains'].items():
                        # Check if domain matches or if no specific domain was given
                        if domain_name is None or domain_data['domain_name'] == domain_name:
                            for command_name, command_data in domain_data['commands'].items():
                                pid = command_data.get('pid')
                                
                                # Only attempt to stop running processes
                                if pid and command_data.get('status') in ['running', 'pending']:
                                    try:
                                        # Use psutil to terminate process and its children
                                        process = psutil.Process(pid)
                                        for child_process in process.children(recursive=True):
                                            child_process.terminate()
                                        process.terminate()
                                        
                                        # Update the status in the data structure
                                        command_data['status'] = 'stopped'
                                        command_data['stop_time'] = time_day_date
                                        
                                        stopped_processes.append({
                                            'group': group_data['group_name'],
                                            'domain': domain_data['domain_name'],
                                            'command': command_name,
                                            'pid': pid
                                        })
                                        
                                        logging.info(f"Stopped process {pid} for {command_name} on {domain_data['domain_name']}")
                                    
                                    except psutil.NoSuchProcess:
                                        # Process already ended
                                        command_data['status'] = 'completed'
                                        logging.warning(f"Process {pid} for {command_name} no longer exists")
                                    
                                    except Exception as stop_error:
                                        not_found_processes.append({
                                            'group': group_data['group_name'],
                                            'domain': domain_data['domain_name'],
                                            'command': command_name,
                                            'pid': pid,
                                            'error': str(stop_error)
                                        })
                                        logging.error(f"Could not stop process {pid}: {stop_error}")

            # Save the updated data
            data_manager_obj.write_to_file(data)

            # Prepare and return results
            return {
                "status": "success",
                "stopped_processes": stopped_processes,
                "not_found_processes": not_found_processes
            }

        except Exception as e:
            logging.error(f"Error in stop_processes: {e}")
            return {"status": "error", "message": str(e)}