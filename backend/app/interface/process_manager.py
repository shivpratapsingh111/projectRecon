import subprocess
import os
import time
import signal
import threading
import json
from filelock import FileLock
from datetime import datetime
from typing import List, Tuple, Literal, Dict
from app.interface.json_data_manager import GroupManager
from app.config.config import ROOT_DATA_DIR
from app.logger.logger import setup_logger

logger = setup_logger(__name__, log_file_path='scan', enable_debug=True)

class ProcessManager:
    def __init__(self):
        self.processes_file = os.path.join(ROOT_DATA_DIR, "running_processes.json")
        self.process_lock = FileLock(f"{self.processes_file}.lock")
        self._ensure_process_file_exists()
        self.termination_events = {}  # Track process termination events
    
    def _ensure_process_file_exists(self):
        """Ensure the processes file exists and is properly initialized."""
        with self.process_lock:
            if not os.path.exists(self.processes_file):
                with open(self.processes_file, 'w') as f:
                    json.dump({}, f)

    def add_process(self, pid: int, process_info: dict):
        """Add a process to the shared storage."""
        with self.process_lock:
            try:
                with open(self.processes_file, 'r') as f:
                    processes = json.load(f)
                processes[str(pid)] = process_info
                with open(self.processes_file, 'w') as f:
                    json.dump(processes, f)
            except Exception as e:
                logger.error(f"Error adding process to storage: {str(e)}")

    def remove_process(self, pid: int):
        """Remove a process from the shared storage."""
        with self.process_lock:
            try:
                with open(self.processes_file, 'r') as f:
                    processes = json.load(f)
                processes.pop(str(pid), None)
                with open(self.processes_file, 'w') as f:
                    json.dump(processes, f)
            except Exception as e:
                logger.error(f"Error removing process from storage: {str(e)}")

    def get_process(self, pid: int) -> dict:
        """Get process info from the shared storage."""
        with self.process_lock:
            try:
                with open(self.processes_file, 'r') as f:
                    processes = json.load(f)
                return processes.get(str(pid))
            except Exception as e:
                logger.error(f"Error getting process from storage: {str(e)}")
                return None

    def get_all_processes(self) -> dict:
        """Get all processes from the shared storage."""
        with self.process_lock:
            try:
                with open(self.processes_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error getting all processes from storage: {str(e)}")
                return {}

    def mark_for_termination(self, pid: int):
        """Mark a process as being terminated intentionally."""
        self.termination_events[pid] = True
        # Also store the termination status in the process info
        process_info = self.get_process(pid)
        if process_info:
            process_info['killed'] = True
            self.add_process(pid, process_info)

    def is_marked_for_termination(self, pid: int) -> bool:
        """Check if a process was marked for termination."""
        process_info = self.get_process(pid)
        if process_info:
            return process_info.get('killed', False)
        return self.termination_events.get(pid, False)


class CommandExecutor:
    def __init__(self):
        self.ROOT_DATA_DIR = ROOT_DATA_DIR
        self.group_manager = GroupManager()
        self.process_manager = ProcessManager()
        self.file_lock = FileLock(f"{self.ROOT_DATA_DIR}/data.json.lock")

    def _create_directories(self, group_name: str, domain: str, scan_dir: str) -> str:
        """Create necessary directories for storing command outputs."""
        result_dir = os.path.join(self.ROOT_DATA_DIR, group_name, domain, scan_dir)
        log_dir = os.path.join(result_dir, "logs")
        
        os.makedirs(result_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)
        
        return result_dir
        
    def _get_current_time(self) -> str:
        """Get formatted current time."""
        return datetime.now().strftime("%H:%M:%S, %A, %d-%m-%Y")

    def _check_process_running(self, pid: int) -> bool:
        """Check if a process is still running."""
        try:
            os.kill(pid, 0)
            return True
        except (ProcessLookupError, PermissionError):
            return False

    def _update_process_status(self, pid: int, status: str) -> bool:
        """
        Update the status of a process in the data manager.
        
        Args:
            pid (int): Process ID
            status (str): New status ('killed', 'error', etc.)
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            # Find the command details by PID using json_data_manager
            command_info = self.group_manager.find_command_by_pid(pid)
            
            if command_info:
                # Update command details with new status and completion time
                command_info['command_details'].update({
                    'status': status,
                    'completion_time': self._get_current_time()
                })

                # Add updated command back to the domain
                self.group_manager.add_command_to_domain(
                    command_info['group_uuid'],
                    command_info['domain_uuid'],
                    command_info['command_details']
                )
                logger.info(f"Successfully updated PID {pid} status to {status}")
                return True
            else:
                logger.error(f"No command found with PID {pid}")
            return False

        except Exception as e:
            logger.error(f"Error updating process status for PID {pid}: {str(e)}")
            return False



    def _execute_single_command(self, cmd_name: str, cmd: str, stdout_path: str, stderr_path: str, 
                              group_uuid: str, domain_uuid: str) -> None:
        """Execute a single command and manage its state."""
        try:
            with open(stdout_path, 'a') as stdout_file, open(stderr_path, 'a') as stderr_file:
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=stdout_file,
                    stderr=stderr_file,
                    text=True
                )
                
            command_details = {
                'command_name': cmd_name,
                'pid': process.pid,
                'command': cmd,
                'status': 'running',
                'start_time': self._get_current_time(),
                'stdout_log': stdout_path,
                'stderr_log': stderr_path,
                'return_code': None,
                'completion_time': None
            }
            
            self.group_manager.add_command_to_domain(group_uuid, domain_uuid, command_details)
            
            process_info = {
                'process': process.pid,
                'group_uuid': group_uuid,
                'domain_uuid': domain_uuid,
                'command_name': cmd_name,
                'killed': False  # Initialize killed status
            }
            self.process_manager.add_process(process.pid, process_info)
            
            logger.debug(f"Started command: {cmd_name} with PID: {process.pid}")
            
            process.wait()
            
            return_code = process.returncode
            
            # First check if the process was marked as killed
            if self.process_manager.is_marked_for_termination(process.pid):
                status = 'killed'
            else:
                status = 'completed' if return_code == 0 else 'error'
            
            command_details.update({
                'status': status,
                'return_code': return_code,
                'completion_time': self._get_current_time()
            })
            
            self.group_manager.add_command_to_domain(group_uuid, domain_uuid, command_details)
            self.process_manager.remove_process(process.pid)
            
            if status == "running" and not self._check_process_running(process.pid):
                self._update_process_status(process.pid, 'error')

            logger.debug(f"Command completed: {cmd_name} with status: {status}")
            
        except Exception as e:
            logger.error(f"Error executing command {cmd_name}: {str(e)}")
            command_details = {
                'command_name': cmd_name,
                'command': cmd,
                'status': 'error',
                'start_time': self._get_current_time(),
                'stdout_log': stdout_path,
                'stderr_log': stderr_path,
                'return_code': None,
                'completion_time': self._get_current_time()
            }
            self.group_manager.add_command_to_domain(group_uuid, domain_uuid, command_details)

    def kill_process_by_pid(self, pid, type) -> bool:
        """Kill a specific process by PID."""
        try:
            pid = int(pid)
            process_info = self.process_manager.get_process(pid)
            
            if process_info and self._check_process_running(pid):
                # Mark the process for termination before sending the signal
                self.process_manager.mark_for_termination(pid)
                
                # Immediately update the status to 'killed' in the group manager
                command_info = self.group_manager.find_command_by_pid(pid)
                if command_info:
                    command_info['command_details'].update({
                        'status': 'killed',
                        'completion_time': self._get_current_time()
                    })
                    self.group_manager.add_command_to_domain(
                        command_info['group_uuid'],
                        command_info['domain_uuid'],
                        command_info['command_details']
                    )
                
                os.kill(pid, signal.SIGTERM)
                logger.debug(f"Successfully sent termination signal to process with PID: {pid}")
                self._update_process_status(pid, 'killed')
                return True
            
            if type == "domain":
                self._update_process_status(pid, 'killed')
                return True
            if type == "domain":
                self._update_process_status(pid, 'killed')
                return True

            logger.info(f"No running process found with PID: {pid}")
            return False
            
        except ProcessLookupError:
            logger.error(f"Process with PID {pid} not found")
            return "Not found"
        except Exception as e:
            logger.error(f"Error killing process {pid}: {str(e)}")
            return "Error in killing"


    def kill_domain_processes(self, group_uuid, domain_uuid: str) -> List[int]:
        """Kill all processes running under a domain."""
        killed_pids = []
        try:
            processes = self.process_manager.get_all_processes()
            domain_processes = {pid: info for pid, info in processes.items() 
                              if info['domain_uuid'] == domain_uuid}
            
            for pid_str, process_info in domain_processes.items():
                pid = int(pid_str)
                if self.kill_process_by_pid(pid, "domain") == True:
                    killed_pids.append(pid)
                else:
                    self._update_process_status(pid, 'error')
            
            logger.debug(f"Killed {len(killed_pids)} processes for domain UUID: {domain_uuid}")
            self.group_manager.update_domain_status_by_id(group_uuid, domain_uuid, "completed")
            self.group_manager.update_group_status_by_id(group_uuid, "completed")
            return killed_pids
            
        except Exception as e:
            logger.error(f"Error killing processes for domain {domain_uuid}: {str(e)}")
            return killed_pids

    def kill_group_processes(self, group_uuid: str) -> List[int]:
        """Kill all processes running under a group."""
        killed_pids = []
        try:
            processes = self.process_manager.get_all_processes()
            group_processes = {pid: info for pid, info in processes.items() 
                             if info['group_uuid'] == group_uuid}
            
            for pid_str, process_info in group_processes.items():
                pid = int(pid_str)
                if self.kill_process_by_pid(pid, "group") == True:
                    killed_pids.append(pid)
                else:
                    self._update_process_status(pid, 'error')
            
            logger.debug(f"Killed {len(killed_pids)} processes for group UUID: {group_uuid}")
            return killed_pids
            
        except Exception as e:
            logger.error(f"Error killing processes for group {group_uuid}: {str(e)}")
            return killed_pids

    def execute_commands(self, group_name: str, domain: str, commands: List[Tuple], program_id: str, domain_id: str, scan_dir: str, execution_style: Literal['sequential', 'parallel'] = 'sequential') -> None:
        """Execute commands either sequentially or in parallel."""
        try:
            if not self.group_manager.create_group(group_name, program_id):
                self.group_manager.update_group_status_by_id(program_id, new_status="running")

            if not self.group_manager.add_domain_to_group(program_id, domain, domain_id):
                self.group_manager.remove_domain_by_id(program_id, domain_id)
                self.group_manager.add_domain_to_group(program_id, domain, domain_id)

            self._create_directories(group_name, domain, scan_dir)
            
            if execution_style == 'parallel':
                threads = []
                for cmd_name, cmd, stdout_path, stderr_path in commands:
                    thread = threading.Thread(
                        target=self._execute_single_command,
                        args=(cmd_name, cmd, stdout_path, stderr_path, program_id, domain_id)
                    )
                    threads.append(thread)
                    time.sleep(1)
                    thread.start()
                
                for thread in threads:
                    thread.join()

            else:
                for cmd_name, cmd, stdout_path, stderr_path in commands:
                    self._execute_single_command(cmd_name, cmd, stdout_path, stderr_path, 
                                              program_id, domain_id)
                    
            self.group_manager.update_execution_status(program_id, domain_id)

        except Exception as e:
            logger.error(f"Error in execute_commands: {str(e)}")
            raise


    def get_all_data(self) -> Dict:
        """Get all data from the data manager."""
        with self.file_lock:
            return self.group_manager._read_file()

def run_commands(group_name: str, domain: str, commands: List[Tuple], program_id: str, domain_id: str, scan_dir: str, 
                execution_style: Literal['sequential', 'parallel'] = 'sequential',) -> None:
    """Main function to run commands."""
    executor = CommandExecutor()
    executor.execute_commands(group_name, domain, commands, program_id, domain_id, scan_dir, execution_style)