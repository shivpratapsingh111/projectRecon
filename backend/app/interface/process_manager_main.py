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


def run_command_wrapper(cmd, stdout_log_file, stderr_log_file, domain):
    """
    Standalone function for running commands that can be pickled by multiprocessing.
    
    Args:
        cmd (str): Command to be executed
        stdout_log_file (str): Path to stdout log file
        stderr_log_file (str): Path to stderr log file
        domain (str): Domain being processed
    """
    try:
        # Open log files for stdout and stderr
        with open(stdout_log_file, 'a') as stdout_log, \
            open(stderr_log_file, 'a') as stderr_log:
            # Use subprocess.Popen with separate stdout and stderr
            print(f"Selected Scan Started for: {domain}")
            subprocess_process = subprocess.Popen(
                cmd, 
                shell=True, 
                stdout=stdout_log, 
                stderr=stderr_log,
                start_new_session=True
            )
            # Wait for the subprocess to complete
            subprocess_process.wait()
    except Exception as e:
        logging.error(f"Error executing command for {domain}: {e}")
        raise


class DomainCommandManager:
    def __init__(self, log_dir: str = 'logs'):
        """
        Enhanced initialization with persistent process tracking.
        
        Args:
            log_dir (str): Directory for log files
            tracking_file (str): Path to process tracking JSON file
        """
        # Existing initialization from original code
        self.log_dir = log_dir

        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        tracking_file_path = os.path.join(log_dir, "process_tracking.json")
        # Setup logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'domain_data_manager_obj.log')),
                logging.StreamHandler()
            ]
        )
        
    
    def update_process_status(self, group_name: str):
        """
        Update the status of a specific process.
        
        Args:
            group_name (str): Name of the group
            process_id (str): Unique process identifier
            status (str): New status of the process
        """
        group_uuid = data_manager_obj.get_group_uuid_by_name(group_name)
        
        group_data = data_manager_obj.list_domains_in_group(group_uuid)

        for domain_uuid in group_data.keys():
            pids = data_manager_obj.get_command_pids_from_domain(domain_uuid).values()
            for pid in pids:
                try:
                    print("Pid in update:", pid)
                    # Fetch process using its PID
                    process = psutil.Process(pid)
                    # Check if the process is running, stopped, sleeping, etc.
                    status = process.status()
                except psutil.NoSuchProcess:
                    status = "stopped"
                except psutil.AccessDenied:
                    status = "Access denied"
                except Exception as e:
                    status = f"An error occurred: {e}"

                print(data_manager_obj.update_command_status_by_pid(pid, status))
        

    def check_pid_status(self, pid):
        try:
            # Fetch process using its PID
            process = psutil.Process(pid)
            # Check if the process is running, stopped, sleeping, etc.

            return process.status()
        except psutil.NoSuchProcess:
            return "stopped"
        except psutil.AccessDenied:
            return f"Access denied"
        except Exception as e:
            return f"An error occurred: {e}"


    def _generate_unique_id(self) -> str:
        """Generate a unique identifier."""
        return str(uuid.uuid4())

    def command_executor(self, group_name: str, domain_list: List[str], domain: str, commands: List[tuple], scan_dir: str) -> Dict[str, Any]:
        # Use the existing implementation, but add additional tracking
        execution_results = {}
        
        result = data_manager_obj.get_group_uuid_by_name(group_name) 

        if result is None: # No group found with provided name
            group_uuid = data_manager_obj.create_group(group_name) # Creating new group
            domain_uuid = data_manager_obj.add_domain_to_group(group_uuid, domain)
        else:
            group_uuid = data_manager_obj.get_group_uuid_by_name(group_name) # Get old group_uuid

            result = data_manager_obj.get_domain_by_name(domain) 
            if result is None: # No domain found with provided name
                domain_uuid = data_manager_obj.add_domain_to_group(group_uuid, domain) # Add new group
            else:
                domain_uuid = data_manager_obj.get_domain_by_name(domain).get('domain_uuid') # Get old domain_uuid
                logging.info(f"Domain '{domain}' and Group '{group_name}' both already exist")

        def domain_command_set(domain):
            domain_results = []
            result_dir = f"{root_Data_Dir}/{group_name}/{domain}/{scan_dir}"
            os.makedirs(result_dir, exist_ok=True)
            os.makedirs(f"{root_Data_Dir}/{group_name}/{domain}/{scan_dir}/logs", exist_ok=True)

            for idx, (command_name, cmd, stdout_log_file, stderr_log_file) in enumerate(commands, 1):
                try:
                    # Create multiprocessing process
                    process = multiprocessing.Process(
                        target=run_command_wrapper, 
                        args=(cmd, stdout_log_file, stderr_log_file, domain)
                    )
                    process.start()

                    # Writing to logs file
                    command_status = self.check_pid_status(process.pid)

                    command_details = {
                        "command_name": command_name,
                        "pid": process.pid,
                        "command": cmd,
                        "status": command_status,
                        "start_time": time_day_date
                    }
                    try:
                        print("Command name:", command_name)
                        print("Pid:", process.pid)
                        result = data_manager_obj.add_command_to_domain(domain_uuid, command_details)
                        logging.info(f"Command Details logged for {command_name}")
                    except Exception as e:
                        logging.error(f"Error logging command deatils for {domain}: {e}")



                
                except Exception as e:
                    logging.error(f"Error executing command for {domain}: {e}")
                    raise
            
            return domain_results

        # Rest of the existing implementation remains the same...
        with ThreadPoolExecutor(max_workers=len(domain_list)) as executor:
            future_to_domain = {
                executor.submit(domain_command_set, domain): domain 
                for domain in domain_list
            }
            
            for future in as_completed(future_to_domain):
                domain = future_to_domain[future]
                try:
                    execution_results[domain] = future.result()
                except Exception as e:
                    logging.error(f"Error processing {domain}: {e}")


        return {
            'group_uuid': group_uuid,
            'execution_results': execution_results
        }

    def command_monitor(self, group_name: Optional[str] = None, domain_name: Optional[str] = None) -> Dict:
        """
        Enhanced monitoring method that combines persistent tracking 
        with the original process monitoring mechanism.
        
        Args:
            group_name (str, optional): Name of the group to monitor
            domain_name (str, optional): Specific domain to monitor
        
        Returns:
            Dict: Monitoring results for processes
        """
        monitoring_results = {}

        self.update_process_status(group_name)
        group_uuid = data_manager_obj.get_group_uuid_by_name(group_name)
        return data_manager_obj.get_group_by_uuid(group_uuid)


