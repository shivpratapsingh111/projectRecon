# data_manager.py
import json
import uuid
import os
import inspect

from typing import Dict, Any, Optional
from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='scan', enable_debug = True)
from app.config.config import data_file

class GroupManagementError(Exception):
    """Custom exception for group management operations."""
    pass

class GroupManager:
    def __init__(self):
        """
        Initialize the GroupManager with a specific file path.
        
        Args:
            file_path (str): Path to the JSON file storing group data
        """
        self.file_path = data_file
        self._initialize_file()
    
    def _initialize_file(self):
        """Create or verify JSON file with proper initial structure."""

        initial_data = {"groups": {}}

        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        if not os.path.exists(self.file_path):
            # Create the file with the initial structure if it doesn't exist
            self._write_to_file(initial_data)
            logger.debug(f"Data file initialized {self.file_path}")
        else:
            logger.debug(f"Json Data file exists {self.file_path}")
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)

                # Validate the existing data structure
                if not isinstance(data, dict) or "groups" not in data:
                    logger.error(f"Json data file exists, but is corrupted {self.file_path}")
            except (json.JSONDecodeError, IOError):
                logger.error(f"Json data file is corrupted {self.file_path}")
                logger.error(f"Something went wrong while processing existing json data file {self.file_path}")
                



    def _write_to_file(self, data):
        """Write data to the file."""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)
            # logger.debug(f"Data written to {self.file_path}")
        except IOError as e:
            logger.exception(f"Error writing in {self.file_path}")
            raise GroupManagementError(f"Error writing to file: {e}")
    
    def _read_file(self) -> Dict[str, Any]:
        """
        Read and parse the JSON file.

        Returns:
            Dict: Parsed JSON data
        """
        try:
            with open(self.file_path, 'r') as f:
                content = f.read().strip()
                if not content:
                    logger.warning(f"JSON file {self.file_path} is empty when read.")
                    return {"groups": {}}  # Return default structure if empty
                
                data = json.loads(content)
                return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.exception(f"Error reading {self.file_path}: {e}")
            raise GroupManagementError(f"Error reading file: {e}")

        
    def create_group(self, group_name: str) -> str:
        """
        Create a new group or return existing group UUID.
        
        Args:
            group_name (str): Name of the group to create
        
        Returns:
            str: UUID of the group
        """
        data = self._read_file()
        
        # Check if group name already exists
        for group_uuid, group in data['groups'].items():
            if group['group_name'] == group_name:
                return group_uuid
        
        # Create new group if it doesn't exist
        new_group_uuid = str(uuid.uuid4())
        data['groups'][new_group_uuid] = {
            "group_name": group_name,
            "domains": {}
        }
        
        self._write_to_file(data)
        return new_group_uuid

    def add_domain_to_group(self, group_uuid: str, domain_name: str) -> str:
        """
        Add a domain to a specific group.
        
        Args:
            group_uuid (str): UUID of the group
            domain_name (str): Name of the domain to add
        
        Returns:
            str: UUID of the domain
        """
        data = self._read_file()
        
        if group_uuid not in data['groups']:
            raise GroupManagementError(f"Group with UUID {group_uuid} not found")
        
        # Check if domain exists in group
        for domain_uuid, domain in data['groups'][group_uuid]['domains'].items():
            if domain['domain_name'] == domain_name:
                return domain_uuid
        
        # Create new domain
        new_domain_uuid = str(uuid.uuid4())
        data['groups'][group_uuid]['domains'][new_domain_uuid] = {
            "domain_name": domain_name,
            "commands": {}
        }
        
        self._write_to_file(data)
        return new_domain_uuid

    def add_command_to_domain(self, group_uuid: str, domain_uuid: str, command_details: Dict[str, Any]) -> None:
        """
        Add or update a command in a specific domain.
        
        Args:
            group_uuid (str): UUID of the group
            domain_uuid (str): UUID of the domain
            command_details (Dict): Details of the command
        """
        data = self._read_file()
        
        if group_uuid not in data['groups']:
            logger.error(f"Group with UUID {group_uuid} not found")
            raise GroupManagementError(f"Group with UUID {group_uuid} not found")
            
        if domain_uuid not in data['groups'][group_uuid]['domains']:
            logger.error(f"Domain with UUID {domain_uuid} not found in group")
            raise GroupManagementError(f"Domain with UUID {domain_uuid} not found in group")
        
        command_name = command_details.get('command_name')
        if not command_name:
            logger.error("Command name is required")
            raise GroupManagementError("Command name is required")
            
        # Update or add command
        data['groups'][group_uuid]['domains'][domain_uuid]['commands'][command_name] = command_details
        self._write_to_file(data)

    def get_groups_uuid(self):
        data = self._read_file()

        group_uuids = []

        for group_uuid in data['groups']:
            group_uuids.append(group_uuid)

        return group_uuids


    def get_group_by_uuid(self, group_uuid: str) -> Dict[str, Any]:
        """
        Retrieve a group by its UUID.
        
        Args:
            group_uuid (str): UUID of the group
        
        Returns:
            Dict: Group details
        """
        data = self._read_file()
        
        if group_uuid not in data['groups']:
            logger.error(f"Group with UUID {group_uuid} not found")
            raise GroupManagementError(f"Group with UUID {group_uuid} not found")
        
        return data['groups'][group_uuid]

    def get_domain_by_uuid(self, domain_uuid: str) -> Dict[str, Any]:
        """
        Retrieve a domain by its UUID.
        
        Args:
            domain_uuid (str): UUID of the domain
        
        Returns:
            Dict: Domain details
        """
        data = self._read_file()
        
        for group in data['groups'].values():
            if domain_uuid in group['domains']:
                return group['domains'][domain_uuid]
        logger.error(f"Domain with UUID {domain_uuid} not found")
        raise GroupManagementError(f"Domain with UUID {domain_uuid} not found")

    def get_domain_by_name(self, domain_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a domain by its name.
        
        Args:
            domain_name (str): Name of the domain
        
        Returns:
            Optional[Dict]: Domain details including its UUID and parent group UUID
        """
        data = self._read_file()
        
        for group_uuid, group in data['groups'].items():
            for domain_uuid, domain in group['domains'].items():
                if domain['domain_name'] == domain_name:
                    return {
                        "group_uuid": group_uuid,
                        "domain_uuid": domain_uuid,
                        **domain
                    }
        
        return None

    def get_command_by_name(self, command_name: str) -> Dict[str, Any]:
        """
        Retrieve a command by its name.
        
        Args:
            command_name (str): Name of the command
        
        Returns:
            Dict: Command details including domain and group UUIDs
        """
        data = self._read_file()
        
        for group_uuid, group in data['groups'].items():
            for domain_uuid, domain in group['domains'].items():
                if command_name in domain['commands']:
                    return {
                        "group_uuid": group_uuid,
                        "domain_uuid": domain_uuid,
                        **domain['commands'][command_name]
                    }
        logger.error(f"Command with name {command_name} not found")
        raise GroupManagementError(f"Command with name {command_name} not found")

    def list_groups(self) -> Dict[str, str]:
        """
        List all groups with their UUIDs.
        
        Returns:
            Dict: Mapping of group UUIDs to group names
        """
        data = self._read_file()
        return {uuid: group['group_name'] for uuid, group in data['groups'].items()}

    def list_domains_in_group(self, group_uuid: str) -> Dict[str, str]:
        """
        List all domains in a specific group.
        
        Args:
            group_uuid (str): UUID of the group
        
        Returns:
            Dict: Mapping of domain UUIDs to domain names
        """
        group = self.get_group_by_uuid(group_uuid)
        return {uuid: domain['domain_name'] for uuid, domain in group['domains'].items()}

    def list_commands_in_domain(self, domain_uuid: str) -> Dict[str, Dict[str, Any]]:
        """
        List all commands in a specific domain.
        
        Args:
            domain_uuid (str): UUID of the domain
        
        Returns:
            Dict: Mapping of command names to command details
        """
        domain = self.get_domain_by_uuid(domain_uuid)
        return domain['commands']

    def get_command_pids_from_domain(self, domain_uuid: str) -> Dict[str, int]:
        """
        Retrieve the PIDs of all commands within a specific domain.
        
        Args:
            domain_uuid (str): UUID of the domain
        
        Returns:
            Dict[str, int]: Mapping of command names to their PIDs
        """
        try:
            domain = self.get_domain_by_uuid(domain_uuid)
            command_pids = {}
            
            for command_name, command_details in domain.get('commands', {}).items():
                pid = command_details.get('pid')
                if pid is not None:
                    command_pids[command_name] = pid
            
            return command_pids

        except GroupManagementError as e:
            logger.exception(f"Error retrieving PIDs for domain {domain_uuid}: {e}")
            raise GroupManagementError(f"Error retrieving PIDs for domain {domain_uuid}: {e}")

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
        
        for group_uuid, group in data['groups'].items():
            for domain_uuid, domain in group['domains'].items():
                for command_name, command_details in domain['commands'].items():
                    if command_details.get('pid') == pid:
                        previous_status = command_details['status']
                        command_details['status'] = new_status
                        
                        self._write_to_file(data)
                        
                        return {
                            'group_uuid': group_uuid,
                            'domain_uuid': domain_uuid,
                            'command_name': command_name,
                            'previous_status': previous_status,
                            'new_status': new_status
                        }
        logger.error(f"No command found with PID {pid}")
        raise GroupManagementError(f"No command found with PID {pid}")

    def find_command_by_pid(self, pid: int) -> Dict[str, Any]:
        """
        Find a command's details by its Process ID (PID).
        
        Args:
            pid (int): Process ID to search for
        
        Returns:
            Dict: Command details including group and domain information
        """
        data = self._read_file()
        
        for group_uuid, group in data['groups'].items():
            for domain_uuid, domain in group['domains'].items():
                for command_name, command_details in domain['commands'].items():
                    if command_details.get('pid') == pid:
                        return {
                            'group_uuid': group_uuid,
                            'domain_uuid': domain_uuid,
                            'command_name': command_name,
                            'command_details': command_details
                        }
        logger.error(f"No command found with PID {pid}")
        raise GroupManagementError(f"No command found with PID {pid}")

    def get_group_by_name(self, group_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a group by its name.
        
        Args:
            group_name (str): Name of the group
        
        Returns:
            Optional[Dict]: Group details including its UUID
        """
        data = self._read_file()
        for uuid, group in data['groups'].items():
            if group['group_name'] == group_name:
                return {"uuid": uuid, **group}
        
        return None

    def get_group_uuid_by_name(self, group_name: str) -> Optional[str]:
        """
        Get group UUID by its name.
        
        Args:
            group_name (str): Name of the group
        
        Returns:
            Optional[str]: UUID of the group if found, None otherwise
        """
        group = self.get_group_by_name(group_name)
        return group['uuid'] if group else None

    def debug_print_groups(self):
        """Debug method to print all current groups."""
        data = self._read_file()
        logger.debug("Current Groups: ")
        for uuid, group in data['groups'].items():
            logger.debug(f"UUID: {uuid}, Name: {group['group_name']}")