# process_manager.py
import os
import json
import threading
import multiprocessing
from multiprocessing import Process, Queue
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
from queue import Empty  # Add this import at the top

# Get current date and time
current_datetime = datetime.now()
formatted_day = current_datetime.strftime("%A")
formatted_date = current_datetime.strftime("%d-%m-%Y")
formatted_time = current_datetime.strftime("%H:%M:%S")
time_day_date = f"{formatted_time}, {formatted_day}, {formatted_date}"
data_manager_obj = GroupManager(data_file)

def process_monitor_worker(process: subprocess.Popen, domain: str, command_name: str, status_queue: Queue):
    """
    Monitor a specific process and report status changes.
    """
    try:
        psutil_process = psutil.Process(process.pid)
        last_status = "running"
        
        while psutil_process.is_running() and process.poll() is None:
            try:
                # Check process status
                current_status = "running" if psutil_process.is_running() else "completed"
                
                # Report status change
                if current_status != last_status:
                    status_queue.put({
                        'domain': domain,
                        'command_name': command_name,
                        'pid': process.pid,
                        'status': current_status,
                        'update_time': datetime.now().strftime('%H:%M:%S, %A, %d-%m-%Y')
                    })
                    
                last_status = current_status
                time.sleep(1)
                
            except psutil.NoSuchProcess:
                status_queue.put({
                    'domain': domain,
                    'command_name': command_name,
                    'pid': process.pid,
                    'status': 'terminated',
                    'update_time': datetime.now().strftime('%H:%M:%S, %A, %d-%m-%Y')
                })
                break
        
        # Get final return code
        return_code = process.poll()
        final_status = 'completed' if return_code == 0 else 'error'
        
        status_queue.put({
            'domain': domain,
            'command_name': command_name,
            'pid': process.pid,
            'status': final_status,
            'return_code': return_code,
            'completion_time': datetime.now().strftime('%H:%M:%S, %A, %d-%m-%Y')
        })
        
    except Exception as e:
        status_queue.put({
            'domain': domain,
            'command_name': command_name,
            'pid': process.pid if process else None,
            'status': 'error',
            'error': str(e),
            'update_time': datetime.now().strftime('%H:%M:%S, %A, %d-%m-%Y')
        })

def run_command_with_monitor(cmd: str, stdout_log_file: str, stderr_log_file: str, 
                           domain: str, command_name: str, status_queue: Queue):
    """
    Run a command and monitor its status in real-time.
    """
    try:
        # Ensure log directories exist
        os.makedirs(os.path.dirname(stdout_log_file), exist_ok=True)
        os.makedirs(os.path.dirname(stderr_log_file), exist_ok=True)
        
        with open(stdout_log_file, 'a') as stdout_log, \
             open(stderr_log_file, 'a') as stderr_log:
            
            # Start the process
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                start_new_session=True
            )
            
            # Start monitor thread
            monitor_thread = threading.Thread(
                target=process_monitor_worker,
                args=(process, domain, command_name, status_queue)
            )
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Stream output to log files
            while True:
                stdout_line = process.stdout.readline()
                stderr_line = process.stderr.readline()
                
                if stdout_line == '' and stderr_line == '' and process.poll() is not None:
                    break
                    
                if stdout_line:
                    stdout_log.write(stdout_line)
                    stdout_log.flush()
                if stderr_line:
                    stderr_log.write(stderr_line)
                    stderr_log.flush()
            
            # Wait for monitor thread to complete
            monitor_thread.join(timeout=5)
            
    except Exception as e:
        status_queue.put({
            'domain': domain,
            'command_name': command_name,
            'status': 'error',
            'error': str(e),
            'update_time': datetime.now().strftime('%H:%M:%S, %A, %d-%m-%Y')
        })

class DomainCommandManager:
    def __init__(self):
        self.data_manager = data_manager_obj

    def _process_domain_commands(self, domain: str, group_name: str, commands: List[tuple], 
                               scan_dir: str, result_queue: Queue) -> List[Dict]:
        """
        Process commands for a domain with real-time status updates.
        """
        domain_results = []
        status_queue = Queue()
        processes = []
        
        # Create status update handler thread
        def status_update_handler():
            while True:
                try:
                    status = status_queue.get(timeout=0.1)
                    # Update command status in data manager
                    self._update_command_status(status, group_name)
                    # Forward status to main result queue
                    result_queue.put(status)
                    
                    # Check if all processes are complete
                    if all(not p.is_alive() for p in processes) and status_queue.empty():
                        break
                except Empty:
                    if all(not p.is_alive() for p in processes):
                        break
                    continue
                except Exception as e:
                    logging.error(f"Error in status update handler: {e}")
        
        # Start status handler thread
        status_handler = threading.Thread(target=status_update_handler)
        status_handler.daemon = True
        status_handler.start()
        
        # Launch commands
        for command_name, cmd, stdout_log_file, stderr_log_file in commands:
            try:
                process = Process(
                    target=run_command_with_monitor,
                    args=(cmd, stdout_log_file, stderr_log_file, domain, 
                          command_name, status_queue)
                )
                process.start()
                processes.append(process)
                
                # Report initial status
                status_queue.put({
                    'domain': domain,
                    'command_name': command_name,
                    'pid': process.pid,
                    'status': 'started',
                    'start_time': datetime.now().strftime('%H:%M:%S, %A, %d-%m-%Y')
                })
                
                domain_results.append({
                    'command': command_name,
                    'status': 'started',
                    'pid': process.pid
                })
                
            except Exception as e:
                logging.error(f"Error starting process for {command_name} on {domain}: {e}")
                status_queue.put({
                    'domain': domain,
                    'command_name': command_name,
                    'status': 'error',
                    'error': str(e),
                    'update_time': datetime.now().strftime('%H:%M:%S, %A, %d-%m-%Y')
                })
        
        # Wait for all processes with timeout
        for process in processes:
            process.join(timeout=300)  # 5-minute timeout
            if process.is_alive():
                process.terminate()
        
        # Wait for status handler to process remaining updates
        status_handler.join(timeout=5)
        
        return domain_results


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
            log_dir = f"{root_Data_Dir}/{group_name}"
            full_scan_dir = os.path.join(log_dir, domain, scan_dir)
            if not os.path.exists(full_scan_dir):
                os.makedirs(full_scan_dir, exist_ok=True)
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

    def get_all_data(self):
        return self.data_manager._read_file()
        

    def _get_all_group_name_with_uuid(self):
        return self.data_manager.list_groups()

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