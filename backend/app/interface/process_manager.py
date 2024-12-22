# process_manager.py
import os
import json
import threading
import multiprocessing
import psutil
import uuid
import time
import logging
from datetime import datetime
import subprocess
from typing import Dict, List, Optional, Any
from app.config.config import *
from concurrent.futures import ThreadPoolExecutor, as_completed
# from app.interface.data_manager import *
from app.interface.data_manager import GroupManager

# Get current date and time
current_datetime = datetime.now()
formatted_day = current_datetime.strftime("%A")
formatted_date = current_datetime.strftime("%d-%m-%Y")
formatted_time = current_datetime.strftime("%H:%M:%S")
time_day_date = f"{formatted_time}, {formatted_day}, {formatted_date}"
data_manager_obj = GroupManager(data_file)


def run_command_wrapper(cmd: str, stdout_log_file: str, stderr_log_file: str, domain: str, command_name: str, result_queue: multiprocessing.Queue):
    """
    Enhanced command wrapper that captures process completion and exit status.
    
    Args:
        cmd (str): Command to execute
        stdout_log_file (str): Path to stdout log file
        stderr_log_file (str): Path to stderr log file
        domain (str): Domain name
        command_name (str): Name of the command
        result_queue (multiprocessing.Queue): Queue for storing results
    """
    try:
        with open(stdout_log_file, 'a') as stdout_log, \
             open(stderr_log_file, 'a') as stderr_log:
            
            # Log command start
            start_message = f"\n{'-'*50}\nCommand execution started at {time_day_date}\n{'-'*50}\n"
            stdout_log.write(start_message)
            
            process = subprocess.Popen(
                cmd, 
                shell=True, 
                stdout=stdout_log, 
                stderr=stderr_log,
                start_new_session=True
            )
            
            # Wait for process completion
            return_code = process.wait()
            
            # Log command completion
            end_message = f"\n{'-'*50}\nCommand execution completed at {datetime.now().strftime('%H:%M:%S, %A, %d-%m-%Y')}\n"
            end_message += f"Return code: {return_code}\n{'-'*50}\n"
            stdout_log.write(end_message)
            
            result_queue.put({
                'domain': domain,
                'command_name': command_name,
                'pid': process.pid,
                'return_code': return_code,
                'status': 'completed' if return_code == 0 else 'failed'
            })
            
    except Exception as e:
        logging.error(f"Error executing command for {domain}: {e}")
        result_queue.put({
            'domain': domain,
            'command_name': command_name,
            'status': 'error',
            'error': str(e)
        })

class DomainCommandManager:
    def __init__(self, log_dir: str = 'logs'):
        """
        Initialize the DomainCommandManager.
        
        Args:
            data_manager: Instance of GroupManager for data management
            log_dir (str): Directory for storing logs
        """
        self.data_manager = data_manager_obj
        self.log_dir = log_dir
        self._setup_logging()

    def _setup_logging(self):
        """Set up logging configuration."""
        full_log_dir = os.path.join(self.log_dir, "logs")
        if not os.path.exists(full_log_dir):
            os.makedirs(full_log_dir, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.log_dir, 'main.log')),
                logging.StreamHandler()
            ]
        )

    def initialize_data_structure(self, group_name: str, domain: str, commands: List[tuple]) -> Dict[str, str]:
        """
        Initialize or update data structure for a group and domain.
        
        Args:
            group_name (str): Name of the group
            domain (str): Domain name
            commands (List[tuple]): List of command tuples (name, cmd, stdout_log, stderr_log)
        
        Returns:
            Dict[str, str]: Dictionary containing group_uuid and domain_uuid
        """
        try:
            # Get or create group
            group_uuid = self.data_manager.get_group_uuid_by_name(group_name)
            if not group_uuid:
                group_uuid = self.data_manager.create_group(group_name)
            
            # Add domain to group
            domain_uuid = self.data_manager.add_domain_to_group(group_uuid, domain)
            
            # Add commands to domain
            for command_name, cmd, stdout_log_file, stderr_log_file in commands:
                command_details = {
                    "command_name": command_name,
                    "pid": None,
                    "command": cmd,
                    "status": "pending",
                    "start_time": time_day_date,
                    "stdout_log": stdout_log_file,
                    "stderr_log": stderr_log_file
                }
                self.data_manager.add_command_to_domain(group_uuid, domain_uuid, command_details)
            
            return {
                "group_uuid": group_uuid,
                "domain_uuid": domain_uuid
            }
            
        except Exception as e:
            logging.error(f"Error initializing data structure: {e}")
            raise

    def _process_domain_commands(self, domain: str, group_name: str, commands: List[tuple], 
                               scan_dir: str, result_queue: multiprocessing.Queue) -> List[Dict]:
        """
        Process commands for a specific domain.
        
        Args:
            domain (str): Domain name
            group_name (str): Group name
            commands (List[tuple]): List of command tuples
            scan_dir (str): Directory for scan results
            result_queue (multiprocessing.Queue): Queue for results
            
        Returns:
            List[Dict]: List of command execution results
        """
        domain_results = []
        result_dir = f"{scan_dir}/{group_name}/{domain}"
        os.makedirs(result_dir, exist_ok=True)
        os.makedirs(f"{result_dir}/logs", exist_ok=True)

        processes = []
        for command_name, cmd, stdout_log_file, stderr_log_file in commands:
            try:
                process = multiprocessing.Process(
                    target=run_command_wrapper,
                    args=(cmd, stdout_log_file, stderr_log_file, domain, command_name, result_queue)
                )
                process.start()
                processes.append((process, command_name, cmd))
                
                domain_results.append({
                    'command': command_name,
                    'status': 'started',
                    'pid': process.pid
                })
                
            except Exception as e:
                logging.error(f"Error starting process for {command_name} on {domain}: {e}")
                domain_results.append({
                    'command': command_name,
                    'status': 'error',
                    'error': str(e)
                })

        # Wait for all processes to complete
        for process, command_name, cmd in processes:
            process.join()

        return domain_results

    def command_executor(self, group_name: str, domain_list: List[str], domain: str, 
                        commands: List[tuple], scan_dir: str) -> Dict[str, Any]:
        """
        Execute commands for multiple domains.
        
        Args:
            group_name (str): Name of the group
            domain_list (List[str]): List of domains
            domain (str): Primary domain name
            commands (List[tuple]): List of command tuples
            scan_dir (str): Directory for scan results
            
        Returns:
            Dict[str, Any]: Execution results and process details
        """
        try:

            if not os.path.exists(os.path.join(self.log_dir, f"{domain}/subdomains/logs")):
                os.makedirs(os.path.join(self.log_dir, f"{domain}/subdomains/logs"), exist_ok=True)
            # Initialize or update data structure
            initialization = self.initialize_data_structure(group_name, domain, commands)
            group_uuid = initialization["group_uuid"]
            
            # Create result queue
            result_queue = multiprocessing.Queue()
            
            # Execute commands for each domain
            execution_results = {}
            
            with ThreadPoolExecutor(max_workers=len(domain_list)) as executor:
                future_to_domain = {
                    executor.submit(
                        self._process_domain_commands,
                        domain,
                        group_name,
                        commands,
                        scan_dir,
                        result_queue
                    ): domain for domain in domain_list
                }
                
                for future in as_completed(future_to_domain):
                    domain = future_to_domain[future]
                    try:
                        execution_results[domain] = future.result()
                    except Exception as e:
                        logging.error(f"Error processing {domain}: {e}")
                        execution_results[domain] = {'status': 'error', 'error': str(e)}
            
            # Process results
            queue_results = []
            while not result_queue.empty():
                queue_results.append(result_queue.get())
            
            # Update command statuses
            for result in queue_results:
                self._update_command_status(result, group_name)
            
            return {
                'group_uuid': group_uuid,
                'execution_results': execution_results,
                'process_results': queue_results
            }
            
        except Exception as e:
            logging.error(f"Error in command executor: {e}")
            raise

    def _update_command_status(self, result: Dict[str, Any], group_name: str):
        """
        Update command status in the data manager.
        
        Args:
            result (Dict[str, Any]): Command execution result
            group_name (str): Name of the group
        """
        try:
            group_uuid = self.data_manager.get_group_uuid_by_name(group_name)
            if not group_uuid:
                logging.error(f"Could not find group UUID for {group_name}")
                return
            
            data = self.data_manager._read_file()
            domain_found = False
            
            for domain_uuid, domain_info in data['groups'][group_uuid]['domains'].items():
                if domain_info['domain_name'] == result['domain']:
                    if result['command_name'] in domain_info['commands']:
                        domain_info['commands'][result['command_name']].update({
                            "status": result.get('status', 'unknown'),
                            "pid": result.get('pid'),
                            "return_code": result.get('return_code'),
                            "completion_time": datetime.now().strftime('%H:%M:%S, %A, %d-%m-%Y')
                        })
                        domain_found = True
                        break
            
            if not domain_found:
                logging.error(f"Could not find domain {result['domain']} or command {result['command_name']}")
                return
            
            self.data_manager._write_to_file(data)
            logging.info(f"Updated status for {result['command_name']} on {result['domain']}: {result.get('status', 'unknown')}")
            
        except Exception as e:
            logging.error(f"Error updating command status: {e}")
            logging.error(f"Result details: {result}")
            import traceback
            traceback.print_exc()

    def command_monitor(self, group_name: Optional[str] = None) -> Dict:
        """
        Monitor command statuses for a group.
        
        Args:
            group_name (Optional[str]): Name of the group to monitor
            
        Returns:
            Dict: Group status information
        """
        try:
            if group_name:
                group_uuid = self.data_manager.get_group_uuid_by_name(group_name)
                if not group_uuid:
                    raise ValueError(f"Group {group_name} not found")
                return self.data_manager.get_group_by_uuid(group_uuid)
            else:
                return self.data_manager._read_file()
        except Exception as e:
            logging.error(f"Error monitoring commands: {e}")
            raise

    def stop_processes(self, group_name: Optional[str] = None, domain_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Stop processes for a given group or domain.
        
        Args:
            group_name (Optional[str]): Name of the group
            domain_name (Optional[str]): Name of the domain
            
        Returns:
            Dict[str, Any]: Summary of stopped processes
        """
        if not group_name and not domain_name:
            logging.error("Must provide either group_name or domain_name")
            return {"status": "error", "message": "No group or domain specified"}

        try:
            data = self.data_manager._read_file()
            stopped_processes = []
            not_found_processes = []

            for group_uuid, group_data in data['groups'].items():
                if group_name is None or group_data['group_name'] == group_name:
                    for domain_uuid, domain_data in group_data['domains'].items():
                        if domain_name is None or domain_data['domain_name'] == domain_name:
                            for command_name, command_data in domain_data['commands'].items():
                                pid = command_data.get('pid')
                                
                                if pid and command_data.get('status') in ['running', 'pending']:
                                    try:
                                        process = psutil.Process(pid)
                                        for child in process.children(recursive=True):
                                            child.terminate()
                                        process.terminate()
                                        
                                        command_data['status'] = 'stopped'
                                        command_data['stop_time'] = time_day_date
                                        
                                        stopped_processes.append({
                                            'group': group_data['group_name'],
                                            'domain': domain_data['domain_name'],
                                            'command': command_name,
                                            'pid': pid
                                        })
                                        
                                    except psutil.NoSuchProcess:
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

            self.data_manager._write_to_file(data)
            return {
                "status": "success",
                "stopped_processes": stopped_processes,
                "not_found_processes": not_found_processes
            }

        except Exception as e:
            logging.error(f"Error in stop_processes: {e}")
            return {"status": "error", "message": str(e)}