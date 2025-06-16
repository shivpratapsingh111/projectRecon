# External imports
import subprocess, os, time, signal, threading, json
from filelock import FileLock
from datetime import datetime
from typing import List, Tuple, Literal, Dict

# Internal imports
from app.interface.json_data_manager import ProgramManager
from app.config.config import ROOT_DATA_DIR, LOG_LEVEL_DEBUG
from app.interface.logger import setup_logger

# Initialization
logger = setup_logger(__name__, log_file_path="interface", enable_debug=LOG_LEVEL_DEBUG)


# Logic
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
                with open(self.processes_file, "w") as f:
                    json.dump({}, f)

    def add_process(self, pid: int, process_info: dict):
        """Add a process to the shared storage."""
        with self.process_lock:
            try:
                with open(self.processes_file, "r") as f:
                    processes = json.load(f)
                processes[str(pid)] = process_info
                with open(self.processes_file, "w") as f:
                    json.dump(processes, f)
            except Exception as e:
                logger.error(f"Error adding process to storage: {str(e)}")

    def remove_process(self, pid: int):
        """Remove a process from the shared storage."""
        with self.process_lock:
            try:
                with open(self.processes_file, "r") as f:
                    processes = json.load(f)
                processes.pop(str(pid), None)
                with open(self.processes_file, "w") as f:
                    json.dump(processes, f)
            except Exception as e:
                logger.error(f"Error removing process from storage: {str(e)}")

    def get_process(self, pid: int) -> dict:
        """Get process info from the shared storage."""
        with self.process_lock:
            try:
                with open(self.processes_file, "r") as f:
                    processes = json.load(f)
                return processes.get(str(pid))
            except Exception as e:
                logger.error(f"Error getting process from storage: {str(e)}")
                return None

    def get_all_processes(self) -> dict:
        """Get all processes from the shared storage."""
        with self.process_lock:
            try:
                with open(self.processes_file, "r") as f:
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
            process_info["killed"] = True
            self.add_process(pid, process_info)

    def is_marked_for_termination(self, pid: int) -> bool:
        """Check if a process was marked for termination."""
        process_info = self.get_process(pid)
        if process_info:
            return process_info.get("killed", False)
        return self.termination_events.get(pid, False)


# ---


class CommandExecutor:
    def __init__(self):
        self.ROOT_DATA_DIR = ROOT_DATA_DIR
        self.program_manager = ProgramManager()
        self.process_manager = ProcessManager()
        self.file_lock = FileLock(f"{self.ROOT_DATA_DIR}/data.json.lock")

    def _create_directories(self, program_name: str, domain: str, scan_dir: str) -> str:
        """Create necessary directories for storing command outputs."""
        result_dir = os.path.join(self.ROOT_DATA_DIR, program_name, domain, scan_dir)
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
            command_info = self.program_manager.find_command_by_pid(pid)

            if command_info:
                # Update command details with new status and completion time
                command_info["command_details"].update(
                    {"status": status, "completion_time": self._get_current_time()}
                )

                # Add updated command back to the domain
                self.program_manager.add_command_to_domain(
                    command_info["program_uuid"],
                    command_info["target_uuid"],
                    command_info["command_details"],
                )
                logger.info(f"Successfully updated PID {pid} status to {status}")
                return True
            else:
                logger.error(f"No command found with PID {pid}")
            return False

        except Exception as e:
            logger.error(f"Error updating process status for PID {pid}: {str(e)}")
            return False

    def _execute_single_command(
        self,
        cmd_name: str,
        cmd: str,
        stdout_path: str,
        stderr_path: str,
        program_uuid: str,
        target_uuid: str,
    ) -> None:
        """Execute a single command and manage its state."""
        try:
            with open(stdout_path, "a") as stdout_file, open(
                stderr_path, "a"
            ) as stderr_file:
                process = subprocess.Popen(
                    cmd, shell=True, stdout=stdout_file, stderr=stderr_file, text=True
                )

            command_details = {
                "command_name": cmd_name,
                "pid": process.pid,
                "command": cmd,
                "status": "running",
                "start_time": self._get_current_time(),
                "stdout_log": stdout_path,
                "stderr_log": stderr_path,
                "return_code": None,
                "completion_time": None,
            }

            self.program_manager.add_command_to_domain(
                program_uuid, target_uuid, command_details
            )

            process_info = {
                "process": process.pid,
                "program_uuid": program_uuid,
                "target_uuid": target_uuid,
                "command_name": cmd_name,
                "killed": False,  # Initialize killed status
            }
            self.process_manager.add_process(process.pid, process_info)

            logger.debug(f"Started command: {cmd_name} with PID: {process.pid}")

            process.wait()

            return_code = process.returncode

            # First check if the process was marked as killed
            if self.process_manager.is_marked_for_termination(process.pid):
                status = "killed"
            else:
                status = "completed" if return_code == 0 else "error"

            command_details.update(
                {
                    "status": status,
                    "return_code": return_code,
                    "completion_time": self._get_current_time(),
                }
            )

            self.program_manager.add_command_to_domain(
                program_uuid, target_uuid, command_details
            )
            self.process_manager.remove_process(process.pid)

            if status == "running" and not self._check_process_running(process.pid):
                self._update_process_status(process.pid, "error")

            logger.debug(f"Command completed: {cmd_name} with status: {status}")

        except Exception as e:
            logger.error(f"Error executing command {cmd_name}: {str(e)}")
            command_details = {
                "command_name": cmd_name,
                "command": cmd,
                "status": "error",
                "start_time": self._get_current_time(),
                "stdout_log": stdout_path,
                "stderr_log": stderr_path,
                "return_code": None,
                "completion_time": self._get_current_time(),
            }
            self.program_manager.add_command_to_domain(
                program_uuid, target_uuid, command_details
            )

    def kill_process_by_pid(self, pid, type) -> bool:
        """Kill a specific process by PID."""
        try:
            pid = int(pid)
            process_info = self.process_manager.get_process(pid)

            if process_info and self._check_process_running(pid):
                # Mark the process for termination before sending the signal
                self.process_manager.mark_for_termination(pid)

                # Immediately update the status to 'killed' in the program manager
                command_info = self.program_manager.find_command_by_pid(pid)
                if command_info:
                    command_info["command_details"].update(
                        {
                            "status": "killed",
                            "completion_time": self._get_current_time(),
                        }
                    )
                    self.program_manager.add_command_to_domain(
                        command_info["program_uuid"],
                        command_info["target_uuid"],
                        command_info["command_details"],
                    )

                os.kill(pid, signal.SIGTERM)
                logger.debug(
                    f"Successfully sent termination signal to process with PID: {pid}"
                )
                self._update_process_status(pid, "killed")
                return True

            if type == "domain":
                self._update_process_status(pid, "killed")
                return True
            if type == "program":
                self._update_process_status(pid, "killed")
                return True
            if type == "single":
                self._update_process_status(pid, "killed")
                return True

            logger.info(f"No running process found with PID: {pid}")
            return False

        except ProcessLookupError:
            logger.error(f"Process with PID {pid} not found")
            return False
        except Exception as e:
            logger.error(f"Error killing process {pid}: {str(e)}")
            return False

    def kill_domain_processes(self, program_uuid, target_uuid: str) -> List[int]:
        """Kill all processes running under a domain."""
        killed_pids = []
        try:
            processes = self.process_manager.get_all_processes()
            domain_processes = {
                pid: info
                for pid, info in processes.items()
                if info["target_uuid"] == target_uuid
            }

            for pid_str, process_info in domain_processes.items():
                pid = int(pid_str)
                if self.kill_process_by_pid(pid, "domain") == True:
                    killed_pids.append(pid)
                else:
                    self._update_process_status(pid, "error")

            logger.debug(
                f"Killed {len(killed_pids)} processes for domain UUID: {target_uuid}"
            )
            self.program_manager.update_domain_status_by_id(
                program_uuid, target_uuid, "completed"
            )
            self.program_manager.update_program_status_by_id(program_uuid, "completed")
            return killed_pids

        except Exception as e:
            logger.error(f"Error killing processes for domain {target_uuid}: {str(e)}")
            return killed_pids

    def kill_program_processes(self, program_uuid: str) -> List[int]:
        """Kill all processes running under a program."""
        killed_pids = []
        try:
            processes = self.process_manager.get_all_processes()
            program_processes = {
                pid: info
                for pid, info in processes.items()
                if info["program_uuid"] == program_uuid
            }

            for pid_str, process_info in program_processes.items():
                pid = int(pid_str)
                if self.kill_process_by_pid(pid, "program") == True:
                    killed_pids.append(pid)
                else:
                    self._update_process_status(pid, "error")

            logger.debug(
                f"Killed {len(killed_pids)} processes for program UUID: {program_uuid}"
            )
            return killed_pids

        except Exception as e:
            logger.error(
                f"Error killing processes for program {program_uuid}: {str(e)}"
            )
            return killed_pids

    def execute_commands(
        self,
        program_name: str,
        domain: str,
        commands: List[Tuple],
        program_uuid: str,
        target_uuid: str,
        scan_dir: str,
        execution_style: Literal["sequential", "parallel"] = "sequential",
    ) -> None:
        """Execute commands either sequentially or in parallel."""
        try:
            if not self.program_manager.create_program(program_name, program_uuid):
                self.program_manager.update_program_status_by_id(
                    program_uuid, new_status="running"
                )

            self.program_manager.add_domain_to_program(
                program_uuid, domain, target_uuid
            )
            # if not self.program_manager.add_domain_to_program(program_uuid, domain, target_uuid):
            #     self.program_manager.remove_domain_by_id(program_uuid, target_uuid)
            #     self.program_manager.add_domain_to_program(program_uuid, domain, target_uuid)

            self._create_directories(program_name, domain, scan_dir)

            if execution_style == "parallel":
                threads = []
                for cmd_name, cmd, stdout_path, stderr_path in commands:
                    thread = threading.Thread(
                        target=self._execute_single_command,
                        args=(
                            cmd_name,
                            cmd,
                            stdout_path,
                            stderr_path,
                            program_uuid,
                            target_uuid,
                        ),
                    )
                    threads.append(thread)
                    time.sleep(1)
                    thread.start()

                for thread in threads:
                    thread.join()

            else:
                for cmd_name, cmd, stdout_path, stderr_path in commands:
                    self._execute_single_command(
                        cmd_name,
                        cmd,
                        stdout_path,
                        stderr_path,
                        program_uuid,
                        target_uuid,
                    )

            self.program_manager.update_execution_status(program_uuid, target_uuid)

        except Exception as e:
            logger.error(f"Error in execute_commands: {str(e)}")
            raise

    def get_all_data(self) -> Dict:
        """Get all data from the data manager."""
        with self.file_lock:
            return self.program_manager._read_file()


def run_commands(
    program_name: str,
    domain: str,
    commands: List[Tuple],
    program_uuid: str,
    target_uuid: str,
    scan_dir: str,
    execution_style: Literal["sequential", "parallel"] = "sequential",
) -> None:
    """Main function to run commands."""
    executor = CommandExecutor()
    executor.execute_commands(
        program_name,
        domain,
        commands,
        program_uuid,
        target_uuid,
        scan_dir,
        execution_style,
    )
