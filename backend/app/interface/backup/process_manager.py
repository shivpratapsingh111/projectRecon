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
from contextlib import contextmanager
from filelock import FileLock
from queue import Empty
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

# Assuming these imports exist in your project
from app.config.config import *
from backend.app.interface.json_data_manager import GroupManager
from app.logger.logger import setup_logger

logger = setup_logger(__name__, log_file_path='scan', enable_debug=True)

@dataclass
class ProcessConfig:
    """Configuration settings for process management"""
    MAX_RETRIES: int = 3
    COMMAND_TIMEOUT: int = 300
    MAX_CONCURRENT_DOMAINS: int = 10
    QUEUE_SIZE: int = 1000
    MONITOR_INTERVAL: float = 1.0
    PROCESS_TERMINATION_TIMEOUT: int = 5

class TimeoutError(Exception):
    """Custom timeout exception"""
    pass

@contextmanager
def timeout_context(seconds: int):
    """Context manager for timeouts"""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")

    import signal
    # Set the timeout handler
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        # Disable the alarm
        signal.alarm(0)

class ProcessPoolContext:
    """Context manager for process pools"""
    def __init__(self):
        self.processes = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for process in self.processes:
            if process and process.is_alive():
                process.terminate()
                try:
                    process.join(timeout=ProcessConfig.PROCESS_TERMINATION_TIMEOUT)
                    if process.is_alive():
                        process.kill()
                except Exception as e:
                    logger.error(f"Error cleaning up process: {e}")

def get_formatted_time():
    """Get current formatted time string"""
    current_datetime = datetime.now()
    return current_datetime.strftime("%H:%M:%S, %A, %d-%m-%Y")

def validate_command_result(result: Dict) -> bool:
    """Validate command execution result"""
    required_fields = {'status', 'command_name', 'domain'}
    return all(field in result for field in required_fields)

def process_monitor_worker(process: subprocess.Popen, domain: str, 
                         command_name: str, status_queue: Queue):
    """Monitor a specific process and report status changes."""
    try:
        logger.debug("In try block of process_monitor_worker")
        with timeout_context(ProcessConfig.COMMAND_TIMEOUT):
            logger.debug("In with block of process_monitor_worker")
            psutil_process = psutil.Process(process.pid)
            last_status = "running"
            
            logger.debug(f"Command name: {command_name}, Status: {psutil_process.status()}")
            
            while psutil_process.is_running() and process.poll() is None:
                logger.debug("In while loop of process_monitor_worker")
                logger.debug(f"Command: {command_name}, Status: {psutil_process.status()}")
                time.sleep(2)
                try:
                    current_status = "running" if psutil_process.is_running() else "completed"
                    
                    if current_status != last_status:
                        status_update = {
                            'domain': domain,
                            'command_name': command_name,
                            'pid': process.pid,
                            'status': current_status,
                            'update_time': get_formatted_time()
                        }
                        status_queue.put(status_update)
                        
                    last_status = current_status
                    time.sleep(ProcessConfig.MONITOR_INTERVAL)
                    
                except psutil.NoSuchProcess:
                    status_queue.put({
                        'domain': domain,
                        'command_name': command_name,
                        'pid': process.pid,
                        'status': 'terminated',
                        'update_time': get_formatted_time()
                    })
                    break
            
            return_code = process.poll()
            final_status = 'completed' if return_code == 0 else 'error'
            
            status_queue.put({
                'domain': domain,
                'command_name': command_name,
                'pid': process.pid,
                'status': final_status,
                'return_code': return_code,
                'completion_time': get_formatted_time()
            })
            
    except TimeoutError:
        logger.debug("In except block process_monitor_worker")
        status_queue.put({
            'domain': domain,
            'command_name': command_name,
            'pid': process.pid,
            'status': 'timeout',
            'error': f'Command exceeded {ProcessConfig.COMMAND_TIMEOUT}s timeout',
            'update_time': get_formatted_time()
        })
    except Exception as e:
        status_queue.put({
            'domain': domain,
            'command_name': command_name,
            'pid': process.pid if process else None,
            'status': 'error',
            'error': str(e),
            'update_time': get_formatted_time()
        })

def run_command_with_retries(cmd: str, stdout_log_file: str, stderr_log_file: str,
                           domain: str, command_name: str, status_queue: Queue):
    """Run a command with retry logic"""
    for attempt in range(ProcessConfig.MAX_RETRIES):
        try:
            return run_command_with_monitor(
                cmd, stdout_log_file, stderr_log_file,
                domain, command_name, status_queue
            )
        except Exception as e:
            if attempt == ProcessConfig.MAX_RETRIES - 1:
                raise
            logger.warning(f"Retry {attempt + 1} for command {command_name}: {e}")
            time.sleep(2 ** attempt)

def run_command_with_monitor(cmd: str, stdout_log_file: str, stderr_log_file: str,
                           domain: str, command_name: str, status_queue: Queue):
    """Run a command and monitor its status in real-time."""
    try:
        os.makedirs(os.path.dirname(stdout_log_file), exist_ok=True)
        os.makedirs(os.path.dirname(stderr_log_file), exist_ok=True)
        
        with open(stdout_log_file, 'a') as stdout_log, \
             open(stderr_log_file, 'a') as stderr_log:
            
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                start_new_session=True
            )
            
            monitor_thread = threading.Thread(
                target=process_monitor_worker,
                args=(process, domain, command_name, status_queue)
            )
            monitor_thread.daemon = True
            monitor_thread.start()
            logger.debug("Called process_monitor_worker")
            
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
            
            monitor_thread.join(timeout=5)
            
    except Exception as e:
        status_queue.put({
            'domain': domain,
            'command_name': command_name,
            'status': 'error',
            'error': str(e),
            'update_time': get_formatted_time()
        })

class DomainCommandManager:
    def __init__(self):
        self.data_manager = GroupManager()
        self.file_lock = FileLock("data.json.lock")

    def _process_domain_commands(self, domain: str, group_name: str,
                               commands: List[tuple], scan_dir: str,
                               result_queue: Queue) -> List[Dict]:
        """Process commands for a domain with real-time status updates."""
        domain_results = []
        status_queue = Queue(maxsize=ProcessConfig.QUEUE_SIZE)
        
        with ProcessPoolContext() as pool:
            processes = []
            
            def status_update_handler():
                while True:
                    try:
                        status = status_queue.get(timeout=0.1)
                        if validate_command_result(status):
                            self._update_command_status(status, group_name)
                            result_queue.put(status)
                        
                        if all(not p.is_alive() for p in processes) and status_queue.empty():
                            break
                    except Empty:
                        if all(not p.is_alive() for p in processes):
                            break
                        continue
                    except Exception as e:
                        logger.exception(f"Error in status update handler: {e}")

            status_handler = threading.Thread(target=status_update_handler)
            status_handler.daemon = True
            status_handler.start()
            
            for command_name, cmd, stdout_log_file, stderr_log_file in commands:
                try:
                    process = Process(
                        target=run_command_with_retries,
                        args=(cmd, stdout_log_file, stderr_log_file,
                              domain, command_name, status_queue)
                    )
                    process.start()
                    processes.append(process)
                    pool.processes.append(process)
                    
                    status_queue.put({
                        'domain': domain,
                        'command_name': command_name,
                        'pid': process.pid,
                        'status': 'started',
                        'start_time': get_formatted_time()
                    })
                    
                    domain_results.append({
                        'command': command_name,
                        'status': 'started',
                        'pid': process.pid
                    })
                    
                except Exception as e:
                    logger.exception(f"Error starting process for {command_name} on {domain}: {e}")
                    status_queue.put({
                        'domain': domain,
                        'command_name': command_name,
                        'status': 'error',
                        'error': str(e),
                        'update_time': get_formatted_time()
                    })
            
            status_handler.join(timeout=5)
            
        return domain_results

    def _update_command_status(self, result: Dict[str, Any], group_name: str):
        """Update command status in the data manager with file locking."""
        with self.file_lock:
            try:
                group_uuid = self.data_manager.get_group_uuid_by_name(group_name)
                if not group_uuid:
                    logger.error(f"Could not find group UUID for {group_name}")
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
                                "completion_time": get_formatted_time()
                            })
                            domain_found = True
                            break
                            
                if not domain_found:
                    logger.error(f"Could not find domain {result['domain']} or command {result['command_name']}")
                    return
                
                self.data_manager._write_to_file(data)
                # logger.debug(f"Updated status for {result['command_name']} on {result['domain']}: {result.get('status', 'unknown')}")
                
            except Exception as e:
                logger.exception(f"Error updating command status: {e}")

    def initialize_data_structure(self, group_name: str, domain: str,
                                commands: List[tuple]) -> Dict[str, str]:
        """Initialize or update data structure for a group and domain."""
        with self.file_lock:
            try:
                group_uuid = self.data_manager.get_group_uuid_by_name(group_name)
                if not group_uuid:
                    group_uuid = self.data_manager.create_group(group_name)
                
                domain_uuid = self.data_manager.add_domain_to_group(group_uuid, domain)
                
                for command_name, cmd, stdout_log_file, stderr_log_file in commands:
                    command_details = {
                        "command_name": command_name,
                        "pid": None,
                        "command": cmd,
                        "status": "pending",
                        "start_time": get_formatted_time(),
                        "stdout_log": stdout_log_file,
                        "stderr_log": stderr_log_file
                    }
                    self.data_manager.add_command_to_domain(group_uuid, domain_uuid, command_details)
                
                return {
                    "group_uuid": group_uuid,
                    "domain_uuid": domain_uuid
                }
                
            except Exception as e:
                logger.exception(f"Error initializing data structure: {e}")
                raise


    def command_executor(self, group_name: str, domain_list: List[str],
                        domain: str, commands: List[tuple],
                        scan_dir: str) -> Dict[str, Any]:
        """Execute commands for multiple domains."""
        try:
            log_dir = f"{root_Data_Dir}/{group_name}"
            full_scan_dir = os.path.join(log_dir, domain, scan_dir)
            os.makedirs(full_scan_dir, exist_ok=True)
            
            initialization = self.initialize_data_structure(group_name, domain, commands)
            group_uuid = initialization["group_uuid"]
            
            result_queue = multiprocessing.Queue(maxsize=ProcessConfig.QUEUE_SIZE)
            execution_results = {}
            
            max_workers = min(len(domain_list), ProcessConfig.MAX_CONCURRENT_DOMAINS)
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
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
                        logger.exception(f"Error processing {domain}: {e}")
                        execution_results[domain] = {
                            'status': 'error',
                            'error': str(e)
                        }
            
            queue_results = []
            while not result_queue.empty():
                queue_results.append(result_queue.get())
            
            for result in queue_results:
                if validate_command_result(result):
                    self._update_command_status(result, group_name)
            
            return {
                'group_uuid': group_uuid,
                'execution_results': execution_results,
                'process_results': queue_results
            }
        except Exception as e:
            logger.exception(f"Error in command executor: {e}")
            raise



    def command_monitor(self, group_name: Optional[str] = None) -> Dict:
        """
        Monitor command statuses for a group.
        
        Args:
            group_name (Optional[str]): Name of the group to monitor
            
        Returns:
            Dict: Group status information
        """
  
        with self.file_lock:
            try:
                if group_name:
                    group_uuid = self.data_manager.get_group_uuid_by_name(group_name)
                    if not group_uuid:
                        raise ValueError(f"Group {group_name} not found")
                    return self.data_manager.get_group_by_uuid(group_uuid)
                else:
                    return self.data_manager._read_file()
            except Exception as e:
                logger.exception(f"Error monitoring commands: {e}")
                raise



    def get_all_data(self) -> Dict:
        """Get all data from the data manager."""
        with self.file_lock:
            return self.data_manager._read_file()

    def _get_all_group_name_with_uuid(self) -> Dict[str, str]:
        """Get all group names with their UUIDs."""
        with self.file_lock:
            return self.data_manager.list_groups()

    def stop_processes(self, group_name: Optional[str] = None, 
                      domain_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Stop processes for a given group or domain.
        
        Args:
            group_name (Optional[str]): Name of the group
            domain_name (Optional[str]): Name of the domain
            
        Returns:
            Dict[str, Any]: Summary of stopped processes
        """
        if not group_name and not domain_name:
            logger.error("Must provide either group_name or domain_name")
            return {"status": "error", "message": "No group or domain specified"}

        with self.file_lock:
            try:
                data = self.data_manager._read_file()
                stopped_processes = []
                not_found_processes = []
                errors = []

                for group_uuid, group_data in data['groups'].items():
                    if group_name is None or group_data['group_name'] == group_name:
                        for domain_uuid, domain_data in group_data['domains'].items():
                            if domain_name is None or domain_data['domain_name'] == domain_name:
                                for command_name, command_data in domain_data['commands'].items():
                                    pid = command_data.get('pid')
                                    
                                    if pid and command_data.get('status') in ['running', 'pending']:
                                        try:
                                            process = psutil.Process(pid)
                                            # Get all child processes
                                            children = process.children(recursive=True)
                                            
                                            # Stop children first
                                            for child in children:
                                                try:
                                                    child.terminate()
                                                    child.wait(timeout=ProcessConfig.PROCESS_TERMINATION_TIMEOUT)
                                                    if child.is_alive():
                                                        child.kill()
                                                except psutil.NoSuchProcess:
                                                    pass
                                                except Exception as child_error:
                                                    errors.append({
                                                        'process': 'child',
                                                        'pid': child.pid,
                                                        'error': str(child_error)
                                                    })
                                            
                                            # Stop main process
                                            process.terminate()
                                            process.wait(timeout=ProcessConfig.PROCESS_TERMINATION_TIMEOUT)
                                            if process.is_alive():
                                                process.kill()
                                            
                                            command_data.update({
                                                'status': 'stopped',
                                                'stop_time': get_formatted_time()
                                            })
                                            
                                            stopped_processes.append({
                                                'group': group_data['group_name'],
                                                'domain': domain_data['domain_name'],
                                                'command': command_name,
                                                'pid': pid
                                            })
                                            
                                        except psutil.NoSuchProcess:
                                            command_data.update({
                                                'status': 'completed',
                                                'completion_time': get_formatted_time()
                                            })
                                            logger.warning(f"Process {pid} for {command_name} no longer exists")
                                            
                                        except Exception as stop_error:
                                            not_found_processes.append({
                                                'group': group_data['group_name'],
                                                'domain': domain_data['domain_name'],
                                                'command': command_name,
                                                'pid': pid,
                                                'error': str(stop_error)
                                            })

                # Write updated data back to file
                self.data_manager._write_to_file(data)
                
                return {
                    "status": "success",
                    "stopped_processes": stopped_processes,
                    "not_found_processes": not_found_processes,
                    "errors": errors if errors else None
                }

            except Exception as e:
                logger.exception(f"Error in stop_processes: {e}")
                return {
                    "status": "error",
                    "message": str(e),
                    "stopped_processes": stopped_processes,
                    "not_found_processes": not_found_processes,
                    "errors": errors if errors else None
                }

    def cleanup_stale_processes(self) -> Dict[str, Any]:
        """
        Clean up any stale processes that might have been left running.
        
        Returns:
            Dict[str, Any]: Summary of cleanup operation
        """
        with self.file_lock:
            try:
                data = self.data_manager._read_file()
                cleaned_processes = []
                errors = []

                for group_uuid, group_data in data['groups'].items():
                    for domain_uuid, domain_data in group_data['domains'].items():
                        for command_name, command_data in domain_data['commands'].items():
                            pid = command_data.get('pid')
                            if pid and command_data.get('status') in ['running', 'pending']:
                                try:
                                    if not psutil.pid_exists(pid):
                                        command_data.update({
                                            'status': 'terminated',
                                            'completion_time': get_formatted_time()
                                        })
                                        cleaned_processes.append({
                                            'group': group_data['group_name'],
                                            'domain': domain_data['domain_name'],
                                            'command': command_name,
                                            'pid': pid
                                        })
                                except Exception as e:
                                    errors.append({
                                        'pid': pid,
                                        'error': str(e)
                                    })

                if cleaned_processes:
                    self.data_manager._write_to_file(data)

                return {
                    "status": "success",
                    "cleaned_processes": cleaned_processes,
                    "errors": errors if errors else None
                }

            except Exception as e:
                logger.exception(f"Error in cleanup_stale_processes: {e}")
                return {
                    "status": "error",
                    "message": str(e)
                }