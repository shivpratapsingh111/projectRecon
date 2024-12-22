# data_manager.py
import json
import uuid
import os
from typing import Dict, Any, Optional

class GroupManagementError(Exception):
    """Custom exception for group management operations."""
    pass

class GroupManager:
    def __init__(self, file_path: str):
        """
        Initialize the GroupManager with a specific file path.
        
        Args:
            file_path (str): Path to the JSON file storing group data
        """
        self.file_path = file_path
        
        # Ensure file exists, create if not
        if not os.path.exists(file_path):
            self._initialize_file()
    
    def _initialize_file(self):
        """
        Create an initial empty JSON structure if file doesn't exist.
        """
        # initial_data = {"groups": {}}
        # with open(self.file_path, 'a') as f:
        #     json.dump(initial_data, f, indent=2)
    
    def _read_file(self) -> Dict[str, Any]:
        """
        Read and parse the JSON file.
        
        Returns:
            Dict: Parsed JSON data
        """
        
        try:
            initial_data = ""
            if not os.path.exists(self.file_path):
                with open(self.file_path, 'w') as f:
                    json.dump(initial_data, f, indent=2)
    
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise GroupManagementError(f"Error reading file: {e}")
    
    def write_to_file(self, data: Dict[str, Any]):
        """
        Write data to the JSON file.
        
        Args:
            data (Dict): Data to write to file
        """
        try:
            with open(self.file_path, 'a') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            raise GroupManagementError(f"Error writing to file: {e}")
    
    def create_group(self, group_name: str) -> str:
        """
        Create a new group and return its UUID.
        
        Args:
            group_name (str): Name of the group to create
        
        Returns:
            str: UUID of the newly created group
        """
        data = self._read_file()
        
        # Check if group name already exists
        for existing_uuid, group in data['groups'].items():
            if group['group_name'] == group_name:
                print(f"Debug: Group '{group_name}' already exists with UUID {existing_uuid}")
                return existing_uuid
        
        new_group_uuid = str(uuid.uuid4())
        data['groups'][new_group_uuid] = {
            "group_name": group_name,
            "domains": {}
        }
        
        self.write_to_file(data)
        print(f"Debug: Created new group '{group_name}' with UUID {new_group_uuid}")
        return new_group_uuid
    

    def add_domain_to_group(self, group_uuid: str, domain_name: str) -> str:
        """
        Add a domain to a specific group.
        
        Args:
            group_uuid (str): UUID of the group
            domain_name (str): Name of the domain to add
        
        Returns:
            str: UUID of the newly created domain
        """
        data = self._read_file()
        
        if group_uuid not in data['groups']:
            raise GroupManagementError(f"Group with UUID {group_uuid} not found")
        
        # Check if domain name already exists in this group
        for domain in data['groups'][group_uuid]['domains'].values():
            if domain['domain_name'] == domain_name:
                raise GroupManagementError(f"Domain '{domain_name}' already exists in this group")
        
        new_domain_uuid = str(uuid.uuid4())
        data['groups'][group_uuid]['domains'][new_domain_uuid] = {
            "domain_name": domain_name,
            "commands": {}
        }
        print(f"Debug: Addedd domain '{domain_name}' to group, with UUID {new_domain_uuid}")

        
        self.write_to_file(data)
        return new_domain_uuid
    
    def add_command_to_domain(self, domain_uuid: str, command_details: Dict[str, Any]) -> None:
        """
        Add a command to a specific domain.
        
        Args:
            domain_uuid (str): UUID of the domain
            command_details (Dict): Details of the command to add
        """
        data = self._read_file()
        
        # Find the domain
        domain_found = False
        for group in data['groups'].values():
            if domain_uuid in group['domains']:
                domain = group['domains'][domain_uuid]
                command_name = command_details.get('command_name', '')
                
                if command_name in domain['commands']: # Chcek if the same command was there in the domain.
                    # raise GroupManagementError(f"Command '{command_name}' already exists in this domain")
                    pass
                
                domain['commands'][command_name] = command_details
                domain_found = True
                break
            
        if not domain_found:
            return (f"Domain with UUID {domain_uuid} not found")
        
        self.write_to_file(data)
        return data

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
        
        raise GroupManagementError(f"Domain with UUID {domain_uuid} not found")
    
    def get_domain_by_name(self, domain_name: str) -> Dict[str, Any]:
        """
        Retrieve a domain by its name.
        
        Args:
            domain_name (str): Name of the domain
        
        Returns:
            Dict: Domain details including its UUID and parent group UUID
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

        This method allows you to extract the process IDs (PIDs) for all commands 
        registered in a particular domain. It provides a convenient way to track 
        running processes associated with a specific domain.

        Args:
            domain_uuid (str): The unique identifier of the domain to search

        Returns:
            Dict[str, int]: A dictionary where:
                - Keys are command names
                - Values are their corresponding process IDs (PIDs)

        Raises:
            GroupManagementError: If the domain is not found or has no commands
        """
        try:
            # Retrieve the entire domain details
            domain = self.get_domain_by_uuid(domain_uuid)
            
            # Extract PIDs from commands
            command_pids = {}
            for command_name, command_details in domain.get('commands', {}).items():
                # Safely extract PID, defaulting to None if not present
                pid = command_details.get('pid')
                
                # Only add to dictionary if PID is not None
                if pid is not None:
                    command_pids[command_name] = pid
            
            # Check if any PIDs were found
            if not command_pids:
                print(f"Warning: No PIDs found for domain UUID {domain_uuid}")
            
            return command_pids

        except GroupManagementError as e:
            print(f"Error retrieving PIDs for domain {domain_uuid}: {e}")
            raise



    def update_command_status_by_pid(self, pid: int, new_status: str):
        """
        Update the status of a command based on its Process ID (PID).
        
        This method provides a flexible way to update command status by searching 
        through all groups, domains, and commands to find a matching PID. This is 
        particularly useful in scenarios where you want to track and update the 
        status of a running process across different domains and groups.

        Args:
            pid (int): The Process ID of the command to update
            new_status (str): The new status to set for the command

        Returns:
            Dict[str, Any]: Details of the updated command, including:
                - group_uuid: UUID of the group containing the command
                - domain_uuid: UUID of the domain containing the command
                - command_name: Name of the command that was updated
                - previous_status: Status before the update
                - new_status: Updated status

        Raises:
            GroupManagementError: If no command with the given PID is found
        """
        # Read the entire file data
        data = self._read_file()
        
        # Iterate through groups, domains, and commands to find matching PID
        for group_uuid, group in data['groups'].items():
            for domain_uuid, domain in group['domains'].items():
                for command_name, command_details in domain['commands'].items():
                    # Check if the PID matches
                    if command_details.get('pid') == pid:
                        # Store the previous status for reporting
                        previous_status = command_details['status']
                        
                        # Update the status
                        command_details['status'] = new_status
                        
                        # Write changes to file
                        self.write_to_file(data)
                        
                        # Return detailed information about the update
                        return {
                            'group_uuid': group_uuid,
                            'domain_uuid': domain_uuid,
                            'command_name': command_name,
                            'previous_status': previous_status,
                            'new_status': new_status
                        }
        
        # If no matching PID is found, raise an error
        raise GroupManagementError(f"No command found with PID {pid}")

    # Optional: Add a method to find commands by PID for additional flexibility
    def find_command_by_pid(self, pid: int) -> Dict[str, Any]:
        """
        Find a command's details by its Process ID (PID).
        
        This method allows for retrieving full details of a command 
        based on its PID without modifying its status.

        Args:
            pid (int): The Process ID to search for

        Returns:
            Dict[str, Any]: Comprehensive details of the command, 
            including group and domain information

        Raises:
            GroupManagementError: If no command with the given PID is found
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
        
        raise GroupManagementError(f"No command found with PID {pid}")








    def get_group_by_name(self, group_name: str) -> Dict[str, Any]:
        """
        Retrieve a group by its name with extensive error checking.
        
        Args:
            group_name (str): Name of the group
        
        Returns:
            Dict: Group details including its UUID
        """
        data = self._read_file()
        for uuid, group in data['groups'].items():
            if group['group_name'] == group_name:
                result = {"uuid": uuid, **group}
                return result
        
        return None
    
    def get_group_uuid_by_name(self, group_name: str) -> str:
        """
        Get group UUID by its name with extensive error handling.
        
        Args:
            group_name (str): Name of the group
        
        Returns:
            str: UUID of the group
        """
        try:
            group = self.get_group_by_name(group_name)
            
            if group is not None:  # Group was found
                uuid = group.get('uuid')  # Get UUID from the group
                return uuid
            else:  # No group found
                return None

        except GroupManagementError as e:
            print(f"Error retrieving UUID for group '{group_name}': {e}")
            raise
    
    def debug_print_groups(self):
        """
        Debug method to print all current groups.
        """
        data = self._read_file()
        print("Current Groups:")
        for uuid, group in data['groups'].items():
            print(f"UUID: {uuid}, Name: {group['group_name']}")

# Example usage with extensive debugging
# manager = GroupManager('groups.json')

# Ensure the group exists
# try:
#     group_uuid = manager.create_group("s")
#     print(f"Group UUID: {group_uuid}")

#     # Verify UUID retrieval
#     retrieved_uuid = manager.get_group_uuid_by_name("s")
#     print(f"Retrieved UUID: {retrieved_uuid}")

#     # Additional debugging
#     manager.debug_print_groups()

# except GroupManagementError as e:
#     print(f"An error occurred: {e}")

