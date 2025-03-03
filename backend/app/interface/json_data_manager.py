# data_manager.py
import json
import uuid
import os
import inspect
import fcntl
from filelock import FileLock, Timeout

import time
from typing import Dict, Any, Optional
from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='scan', enable_debug = True)
from app.config.config import data_file

class GroupManagementError(Exception):
    """Custom exception for group management operations."""
    pass

class GroupManager:
    def __init__(self):
        self.file_path = data_file
        self.lock_file_path = f"{self.file_path}.lock"
        self.lock = FileLock(self.lock_file_path, timeout=10)
        self._initialize_file()

    def _initialize_file(self):
        """Create or verify JSON file with proper initial structure."""
        initial_data = {"groups": {}}
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
            raise GroupManagementError("Lock acquisition timeout")

    def _validate_file(self):
        """Validate the existing file structure."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    logger.warning(f"Empty file found, reinitializing {self.file_path}")
                    self._write_to_file({"groups": {}})
                    return

                data = json.loads(content)
                if not isinstance(data, dict) or "groups" not in data:
                    logger.error(f"Invalid data structure in {self.file_path}")
                    raise GroupManagementError("Invalid data structure")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error validating file {self.file_path}: {e}")
            raise GroupManagementError(f"File validation error: {e}")

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
            raise GroupManagementError("Write operation timeout")
        except IOError as e:
            logger.error(f"Error writing to file: {e}")
            raise GroupManagementError(f"Write error: {e}")

    def update_execution_status(self, group_uuid: str, domain_uuid: str) -> None:
        """Update the status of the domain and group after execution."""
        
        data = self._read_file()
        group_data = data.get("groups", {}).get(group_uuid)
        if not group_data:
            return
        domain_data = group_data.get("domains", {}).get(domain_uuid, {})
        if not domain_data:
            return
        
        # Check if all commands in the domain are completed
        domain_completed = all(cmd["status"] != "running" for cmd in domain_data.get("commands", {}).values())
        
        # If domain is completed, update its status
        if domain_completed:
            domain_data["status"] = "completed"
            
            # Check if all domains in the group are completed
            group_completed = all(dom.get("status") != "running" for dom in group_data["domains"].values())
            
            # If group is completed, update its status
            if group_completed:
                group_data["status"] = "completed"
            else:
                group_data["status"] = "running"

        
        # Open file and update only relevant parts
        with open(self.file_path, "r+") as file:
            file_data = json.load(file)
            file_data["groups"][group_uuid]["domains"][domain_uuid]["status"] = domain_data.get("status", "")
            file_data["groups"][group_uuid]["status"] = group_data.get("status", "")
            
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
                        return {"groups": {}}
                    return json.loads(content)
        except Timeout:
            logger.error("Lock acquisition timeout during read operation")
            raise GroupManagementError("Read operation timeout")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading file: {e}")
            raise GroupManagementError(f"Read error: {e}")

        
    def create_group(self, group_name: str, program_id: str) -> str:
        """
        Create a new group or return existing group UUID.
        
        Args:
            group_name (str): Name of the group to create
        
        Returns:
            str: UUID of the group
        """
        data = self._read_file()
        
        
        for group_uuid, group in data['groups'].items():
            if group['group_name'] == group_name:
                logger.debug(f"Group {group_name} already exists with id {group_uuid}")
                return False
        
        new_group_uuid = program_id
        data['groups'][new_group_uuid] = {
            "group_name": group_name,
            "status": "running",
            "domains": {}
        }
        
        self._write_to_file(data)
        return True

    def add_domain_to_group(self, group_uuid: str, domain_name: str, domain_id: str) -> str:
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
        
        for domain_uuid, domain in data['groups'][group_uuid]['domains'].items():
            if domain['domain_name'] == domain_name:
                logger.debug(f"Domain {domain_name} already exists with id {domain_id}")
                return False
        
        new_domain_uuid = domain_id
        data['groups'][group_uuid]['domains'][new_domain_uuid] = {
            "domain_name": domain_name,
            "status": "running",
            "commands": {}
        }
        
        self._write_to_file(data)
        return True

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


    def update_group_status_by_id(self, group_id: str, new_status: str) -> Dict[str, Any]:
        """
        Update the status of a group based on its Group ID.

        Args:
            group_id (str): UUID of the group
            new_status (str): New status to set

        Returns:
            Dict: Details of the updated group
        """
        data = self._read_file()

        if group_id in data["groups"]:
            previous_status = data["groups"][group_id]["status"]
            data["groups"][group_id]["status"] = new_status
            
            self._write_to_file(data)

            return {
                "group_id": group_id,
                "previous_status": previous_status,
                "new_status": new_status
            }

        logger.error(f"No group found with ID {group_id}")
        raise GroupManagementError(f"No group found with ID {group_id}")


    def update_domain_status_by_id(self, group_id: str, domain_id: str, new_status: str) -> Dict[str, Any]:
        """
        Update the status of a domain based on its Group ID and Domain ID.

        Args:
            group_id (str): UUID of the group
            domain_id (str): UUID of the domain
            new_status (str): New status to set

        Returns:
            Dict: Details of the updated domain
        """
        data = self._read_file()

        if group_id in data["groups"]:
            group = data["groups"][group_id]
            if domain_id in group["domains"]:
                previous_status = group["domains"][domain_id]["status"]
                group["domains"][domain_id]["status"] = new_status

                self._write_to_file(data)

                return {
                    "group_id": group_id,
                    "domain_id": domain_id,
                    "previous_status": previous_status,
                    "new_status": new_status
                }

        logger.error(f"No domain found with ID {domain_id} in group {group_id}")
        raise GroupManagementError(f"No domain found with ID {domain_id} in group {group_id}")


    def remove_domain_by_id(self, group_id: str, domain_id: str) -> Dict[str, Any]:
        """
        Remove a domain and all its associated commands from a group.

        Args:
            group_id (str): UUID of the group containing the domain
            domain_id (str): UUID of the domain to remove

        Returns:
            Dict: Details of the removed domain
        """
        data = self._read_file()

        if group_id in data["groups"]:
            group = data["groups"][group_id]
            if domain_id in group["domains"]:
                removed_domain = group["domains"].pop(domain_id)  # Remove domain
                
                self._write_to_file(data)  # Save updated data
                
                return {
                    "group_id": group_id,
                    "removed_domain_id": domain_id,
                    "removed_domain_name": removed_domain.get("domain_name", "Unknown"),
                    "message": "Domain removed successfully"
                }

        logger.error(f"No domain found with ID {domain_id} in group {group_id}")
        raise GroupManagementError(f"No domain found with ID {domain_id} in group {group_id}")

    def remove_group_by_id(self, group_id: str) -> Dict[str, Any]:
        """
        Remove a group and all its associated domains and commands based on Group ID.

        Args:
            group_id (str): UUID of the group to remove

        Returns:
            Dict: Details of the removed group
        """
        data = self._read_file()

        if group_id in data["groups"]:
            removed_group = data["groups"].pop(group_id)  # Remove group
            
            self._write_to_file(data)  # Save updated data
            
            return {
                "removed_group_id": group_id,
                "removed_group_name": removed_group.get("group_name", "Unknown"),
                "message": "Group removed successfully"
            }

        logger.error(f"No group found with ID {group_id}")
        raise GroupManagementError(f"No group found with ID {group_id}")


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