# External imports
import json, os
from filelock import FileLock, Timeout
from typing import Dict, Any, Optional

# Internal imports
from app.interface.logger import setup_logger
from app.config.config import LOG_LEVEL_DEBUG
from app.config.config import PROGRAMS_DATA_FILE
logger = setup_logger(__name__, log_file_path='interface', enable_debug = LOG_LEVEL_DEBUG)

# Logic
class ProgramManagementError(Exception):
    """Custom exception for program management operations."""
    pass

class ProgramManager:
    def __init__(self):
        self.file_path = PROGRAMS_DATA_FILE
        self.lock_file_path = f"{self.file_path}.lock"
        self.lock = FileLock(self.lock_file_path, timeout=10)
        self._initialize_file()

    def _initialize_file(self):
        """Create or verify JSON file with proper initial structure."""
        initial_data = {"programs": {}}
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        try:
            with self.lock:
                if not os.path.exists(self.file_path):
                    with open(self.file_path, 'w', encoding='utf-8') as f:
                        json.dump(initial_data, f, indent=2)
                    logger.debug(f"Data file initialized {self.file_path}")
                else:
                    self._validate_file()
        except Timeout:
            logger.error(f"Could not acquire lock for {self.file_path} within the timeout period")
            raise ProgramManagementError("Lock acquisition timeout")

    def _validate_file(self):
        """Validate the existing file structure."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    logger.warning(f"Empty file found, reinitializing {self.file_path}")
                    self._write_to_file({"programs": {}})
                    return

                data = json.loads(content)
                if not isinstance(data, dict) or "programs" not in data:
                    logger.error(f"Invalid data structure in {self.file_path}")
                    raise ProgramManagementError("Invalid data structure")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error validating file {self.file_path}: {e}")
            raise ProgramManagementError(f"File validation error: {e}")

    def _write_to_file(self, data: Dict[str, Any], file_path = None):
        """Write data to file with proper locking."""
        if file_path is None:
            file_path = self.file_path
        try:
            with self.lock:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
        except Timeout:
            logger.error("Lock acquisition timeout during write operation")
            raise ProgramManagementError("Write operation timeout")
        except IOError as e:
            logger.error(f"Error writing to file: {e}")
            raise ProgramManagementError(f"Write error: {e}")

    def update_execution_status(self, program_uuid: str, target_uuid: str) -> None:
        """Update the status of the domain and program after execution."""
        
        data = self._read_file()
        program_data = data.get("programs", {}).get(program_uuid)
        if not program_data:
            return
        domain_data = program_data.get("domains", {}).get(target_uuid, {})
        if not domain_data:
            return
        
        # Check if all commands in the domain are completed
        domain_completed = all(cmd["status"] != "running" for cmd in domain_data.get("commands", {}).values())
        
        # If domain is completed, update its status
        if domain_completed:
            domain_data["status"] = "completed"
            
            # Check if all domains in the program are completed
            program_completed = all(dom.get("status") != "running" for dom in program_data["domains"].values())
            
            # If program is completed, update its status
            if program_completed:
                program_data["status"] = "completed"
            else:
                program_data["status"] = "running"

        
        # Open file and update only relevant parts
        with open(self.file_path, "r+") as file:
            file_data = json.load(file)
            file_data["programs"][program_uuid]["domains"][target_uuid]["status"] = domain_data.get("status", "")
            file_data["programs"][program_uuid]["status"] = program_data.get("status", "")
            
            file.seek(0)  # Move cursor to the beginning
            json.dump(file_data, file, indent=4)
            file.truncate()  # Remove excess data if file size shrinks


    def _read_file(self, file_path = None) -> Dict[str, Any]:
        """Read data from file with proper locking."""
        if file_path is None:
            file_path = self.file_path
        try:
            with self.lock:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        logger.warning(f"Empty file found during read {file_path}")
                        return {"programs": {}}
                    return json.loads(content)
        except Timeout:
            logger.error("Lock acquisition timeout during read operation")
            raise ProgramManagementError("Read operation timeout")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading file: {e}")
            raise ProgramManagementError(f"Read error: {e}")

        
    def create_program(self, program_name: str, program_uuid: str) -> str:
        """
        Create a new program or return existing program UUID.
        
        Args:
            program_name (str): Name of the program to create
        
        Returns:
            str: UUID of the program
        """
        data = self._read_file()
        
        
        for id, program in data['programs'].items():
            if program['program_name'] == program_name:
                logger.debug(f"Program {program_name} already exists with id {program_uuid}")
                return False
        
        new_program_uuid = program_uuid

        data['programs'][new_program_uuid] = {
            "program_name": program_name,
            "status": "running",
            "domains": {}
        }
        
        self._write_to_file(data)
        return True

    def add_domain_to_program(self, program_uuid: str, domain_name: str, target_uuid: str) -> str:
        """
        Add a domain to a specific program.
        
        Args:
            program_uuid (str): UUID of the program
            domain_name (str): Name of the domain to add
        
        Returns:
            str: UUID of the domain
        """
        data = self._read_file()
        
        if program_uuid not in data['programs']:
            raise ProgramManagementError(f"Program with UUID {program_uuid} not found")
        
        for target_uuid, domain in data['programs'][program_uuid]['domains'].items():
            if domain['domain_name'] == domain_name:
                logger.debug(f"Domain {domain_name} already exists with id {target_uuid}")
                return False
        
        new_target_uuid = target_uuid
        data['programs'][program_uuid]['domains'][new_target_uuid] = {
            "domain_name": domain_name,
            "status": "running",
            "commands": {}
        }
        
        self._write_to_file(data)
        return True

    def add_command_to_domain(self, program_uuid: str, target_uuid: str, command_details: Dict[str, Any]) -> None:
        """
        Add or append a command to a specific domain.
        
        Args:
            program_uuid (str): UUID of the program
            target_uuid (str): UUID of the domain
            command_details (Dict): Details of the command
        """
        data = self._read_file()
        
        if program_uuid not in data['programs']:
            logger.error(f"Program with UUID {program_uuid} not found")
            raise ProgramManagementError(f"Program with UUID {program_uuid} not found")
            
        if target_uuid not in data['programs'][program_uuid]['domains']:
            logger.error(f"Domain with UUID {target_uuid} not found in program")
            raise ProgramManagementError(f"Domain with UUID {target_uuid} not found in program")
        
        command_name = command_details.get('command_name')
        if not command_name:
            logger.error("Command name is required")
            raise ProgramManagementError("Command name is required")
        
        data['programs'][program_uuid]['domains'][target_uuid]['commands'][command_name] = command_details
        self._write_to_file(data)

    def get_programs_uuid(self):
        data = self._read_file()

        program_uuids = []

        for program_uuid in data['programs']:
            program_uuids.append(program_uuid)

        return program_uuids


    def get_program_by_uuid(self, program_uuid: str) -> Dict[str, Any]:
        """
        Retrieve a program by its UUID.
        
        Args:
            program_uuid (str): UUID of the program
        
        Returns:
            Dict: Program details
        """
        data = self._read_file()
        
        if program_uuid not in data['programs']:
            logger.error(f"Program with UUID {program_uuid} not found")
            raise ProgramManagementError(f"Program with UUID {program_uuid} not found")
        
        return data['programs'][program_uuid]

    def get_domain_by_uuid(self, target_uuid: str) -> Dict[str, Any]:
        """
        Retrieve a domain by its UUID.
        
        Args:
            target_uuid (str): UUID of the domain
        
        Returns:
            Dict: Domain details
        """
        data = self._read_file()
        
        for program in data['programs'].values():
            if target_uuid in program['domains']:
                return program['domains'][target_uuid]
        logger.error(f"Domain with UUID {target_uuid} not found")
        raise ProgramManagementError(f"Domain with UUID {target_uuid} not found")

    def get_domain_by_name(self, domain_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a domain by its name.
        
        Args:
            domain_name (str): Name of the domain
        
        Returns:
            Optional[Dict]: Domain details including its UUID and parent program UUID
        """
        data = self._read_file()
        
        for program_uuid, program in data['programs'].items():
            for target_uuid, domain in program['domains'].items():
                if domain['domain_name'] == domain_name:
                    return {
                        "program_uuid": program_uuid,
                        "target_uuid": target_uuid,
                        **domain
                    }
        
        return None

    def get_command_by_name(self, command_name: str) -> Dict[str, Any]:
        """
        Retrieve a command by its name.
        
        Args:
            command_name (str): Name of the command
        
        Returns:
            Dict: Command details including domain and program UUIDs
        """
        data = self._read_file()
        
        for program_uuid, program in data['programs'].items():
            for target_uuid, domain in program['domains'].items():
                if command_name in domain['commands']:
                    return {
                        "program_uuid": program_uuid,
                        "target_uuid": target_uuid,
                        **domain['commands'][command_name]
                    }
        logger.error(f"Command with name {command_name} not found")
        raise ProgramManagementError(f"Command with name {command_name} not found")

    def list_programs(self) -> Dict[str, str]:
        """
        List all programs with their UUIDs.
        
        Returns:
            Dict: Mapping of program UUIDs to program names
        """
        data = self._read_file()
        return {uuid: program['program_name'] for uuid, program in data['programs'].items()}

    def list_domains_in_program(self, program_uuid: str) -> Dict[str, str]:
        """
        List all domains in a specific program.
        
        Args:
            program_uuid (str): UUID of the program
        
        Returns:
            Dict: Mapping of domain UUIDs to domain names
        """
        program = self.get_program_by_uuid(program_uuid)
        return {uuid: domain['domain_name'] for uuid, domain in program['domains'].items()}

    def list_commands_in_domain(self, target_uuid: str) -> Dict[str, Dict[str, Any]]:
        """
        List all commands in a specific domain.
        
        Args:
            target_uuid (str): UUID of the domain
        
        Returns:
            Dict: Mapping of command names to command details
        """
        domain = self.get_domain_by_uuid(target_uuid)
        return domain['commands']

    def get_command_pids_from_domain(self, target_uuid: str) -> Dict[str, int]:
        """
        Retrieve the PIDs of all commands within a specific domain.
        
        Args:
            target_uuid (str): UUID of the domain
        
        Returns:
            Dict[str, int]: Mapping of command names to their PIDs
        """
        try:
            domain = self.get_domain_by_uuid(target_uuid)
            command_pids = {}
            
            for command_name, command_details in domain.get('commands', {}).items():
                pid = command_details.get('pid')
                if pid is not None:
                    command_pids[command_name] = pid
            
            return command_pids

        except ProgramManagementError as e:
            logger.exception(f"Error retrieving PIDs for domain {target_uuid}: {e}")
            raise ProgramManagementError(f"Error retrieving PIDs for domain {target_uuid}: {e}")

    def update_command_status_by_pid(self, pid: int, new_status: str) -> Dict[str, Any]:
        """
        Update the status of a command based on its Process ID (PID).
        
        Args:
            pid (int): Process ID of the command
            new_status (str): New status to set
        
        Returns:
            Dict: Details of the updated command
        """
        data = self._read_file()
        
        for program_uuid, program in data['programs'].items():
            for target_uuid, domain in program['domains'].items():
                for command_name, command_details in domain['commands'].items():
                    if command_details.get('pid') == pid:
                        previous_status = command_details['status']
                        command_details['status'] = new_status
                        
                        self._write_to_file(data)
                        
                        return {
                            'program_uuid': program_uuid,
                            'target_uuid': target_uuid,
                            'command_name': command_name,
                            'previous_status': previous_status,
                            'new_status': new_status
                        }
        logger.error(f"No command found with PID {pid}")
        raise ProgramManagementError(f"No command found with PID {pid}")


    def update_program_status_by_id(self, program_uuid: str, new_status: str) -> Dict[str, Any]:
        """
        Update the status of a program based on its Program ID.

        Args:
            program_uuid (str): UUID of the program
            new_status (str): New status to set

        Returns:
            Dict: Details of the updated program
        """
        data = self._read_file()

        if program_uuid in data["programs"]:
            previous_status = data["programs"][program_uuid]["status"]
            data["programs"][program_uuid]["status"] = new_status
            
            self._write_to_file(data)

            return {
                "program_uuid": program_uuid,
                "previous_status": previous_status,
                "new_status": new_status
            }

        logger.error(f"No program found with ID {program_uuid}")
        raise ProgramManagementError(f"No program found with ID {program_uuid}")


    def update_domain_status_by_id(self, program_uuid: str, target_uuid: str, new_status: str) -> Dict[str, Any]:
        """
        Update the status of a domain based on its Program ID and Domain ID.

        Args:
            program_uuid (str): UUID of the program
            target_uuid (str): UUID of the domain
            new_status (str): New status to set

        Returns:
            Dict: Details of the updated domain
        """
        data = self._read_file()

        if program_uuid in data["programs"]:
            program = data["programs"][program_uuid]
            if target_uuid in program["domains"]:
                previous_status = program["domains"][target_uuid]["status"]
                program["domains"][target_uuid]["status"] = new_status

                self._write_to_file(data)

                return {
                    "program_uuid": program_uuid,
                    "target_uuid": target_uuid,
                    "previous_status": previous_status,
                    "new_status": new_status
                }

        logger.error(f"No domain found with ID {target_uuid} in program {program_uuid}")
        raise ProgramManagementError(f"No domain found with ID {target_uuid} in program {program_uuid}")


    def remove_domain_by_id(self, program_uuid: str, target_uuid: str) -> Dict[str, Any]:
        """
        Remove a domain and all its associated commands from a program.

        Args:
            program_uuid (str): UUID of the program containing the domain
            target_uuid (str): UUID of the domain to remove

        Returns:
            Dict: Details of the removed domain
        """
        data = self._read_file()

        if program_uuid in data["programs"]:
            program = data["programs"][program_uuid]
            if target_uuid in program["domains"]:
                removed_domain = program["domains"].pop(target_uuid)  # Remove domain
                
                self._write_to_file(data)  # Save updated data
                
                return {
                    "program_uuid": program_uuid,
                    "removed_target_uuid": target_uuid,
                    "removed_domain_name": removed_domain.get("domain_name", "Unknown"),
                    "message": "Domain removed successfully"
                }

        logger.error(f"No domain found with ID {target_uuid} in program {program_uuid}")
        raise ProgramManagementError(f"No domain found with ID {target_uuid} in program {program_uuid}")

    def remove_program_by_id(self, program_uuid: str) -> Dict[str, Any]:
        """
        Remove a program and all its associated domains and commands based on Program ID.

        Args:
            program_uuid (str): UUID of the program to remove

        Returns:
            Dict: Details of the removed program
        """
        data = self._read_file()

        if program_uuid in data["programs"]:
            removed_program = data["programs"].pop(program_uuid)  # Remove program
            
            self._write_to_file(data)  # Save updated data
            
            return {
                "removed_program_uuid": program_uuid,
                "removed_program_name": removed_program.get("program_name", "Unknown"),
                "message": "Program removed successfully"
            }

        logger.error(f"No program found with ID {program_uuid}")
        raise ProgramManagementError(f"No program found with ID {program_uuid}")


    def find_command_by_pid(self, pid: int) -> Dict[str, Any]:
        """
        Find a command's details by its Process ID (PID).
        
        Args:
            pid (int): Process ID to search for
        
        Returns:
            Dict: Command details including program and domain information
        """
        data = self._read_file()
        
        for program_uuid, program in data['programs'].items():
            for target_uuid, domain in program['domains'].items():
                for command_name, command_details in domain['commands'].items():
                    if command_details.get('pid') == pid:
                        return {
                            'program_uuid': program_uuid,
                            'target_uuid': target_uuid,
                            'command_name': command_name,
                            'command_details': command_details
                        }
        logger.error(f"No command found with PID {pid}")
        raise ProgramManagementError(f"No command found with PID {pid}")

    def get_program_by_name(self, program_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a program by its name.
        
        Args:
            program_name (str): Name of the program
        
        Returns:
            Optional[Dict]: Program details including its UUID
        """
        data = self._read_file()
        for uuid, program in data['programs'].items():
            if program['program_name'] == program_name:
                return {"uuid": uuid, **program}
        
        return None

    def get_program_uuidby_name(self, program_name: str) -> Optional[str]:
        """
        Get program UUID by its name.
        
        Args:
            program_name (str): Name of the program
        
        Returns:
            Optional[str]: UUID of the program if found, None otherwise
        """
        program = self.get_program_by_name(program_name)
        return program['uuid'] if program else None

    def debug_print_programs(self):
        """Debug method to print all current programs."""
        data = self._read_file()
        logger.debug("Current programs: ")
        for uuid, program in data['programs'].items():
            logger.debug(f"UUID: {uuid}, Name: {program['program_name']}")