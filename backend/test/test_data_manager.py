import json
import uuid
import os
from typing import Dict, Any, Optional

class ProgramManagementError(Exception):
    """Custom exception for Program management operations."""
    pass

class ProgramManager:
    def __init__(self, file_path: str):
        """
        Initialize the ProgramManager with a specific file path.
        
        Args:
            file_path (str): Path to the JSON file storing Program data
        """
        self.file_path = file_path
        
        # Ensure file exists, create if not
        if not os.path.exists(file_path):
            self._initialize_file()
    
    def _initialize_file(self):
        """
        Create an initial empty JSON structure if file doesn't exist.
        """
        initial_data = {"programs": {}}
        with open(self.file_path, 'w') as f:
            json.dump(initial_data, f, indent=2)
    
    def _read_file(self) -> Dict[str, Any]:
        """
        Read and parse the JSON file.
        
        Returns:
            Dict: Parsed JSON data
        """
        
        try:
            initial_data = {"programs": {}}
            if not os.path.exists(self.file_path):
                with open(self.file_path, 'w') as f:
                    json.dump(initial_data, f, indent=2)
    
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ProgramManagementError(f"Error reading file: {e}")
    
    def write_to_file(self, data: Dict[str, Any]):
        """
        Write data to the JSON file.
        
        Args:
            data (Dict): Data to write to file
        """
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            raise ProgramManagementError(f"Error writing to file: {e}")
    
    def create_program(self, program_name: str) -> str:
        """
        Create a new Program and return its UUID.
        
        Args:
            program_name (str): Name of the Program to create
        
        Returns:
            str: UUID of the newly created Program
        """
        data = self._read_file()
        
        # Check if Program name already exists
        for existing_uuid, Program in data['programs'].items():
            if Program['program_name'] == program_name:
                print(f"Debug: Program '{program_name}' already exists with UUID {existing_uuid}")
                return existing_uuid
        
        new_program_uuid = str(uuid.uuid4())
        data['programs'][new_program_uuid] = {
            "program_name": program_name,
            "domains": {}
        }
        
        self.write_to_file(data)
        print(f"Debug: Created new Program '{program_name}' with UUID {new_program_uuid}")
        return new_program_uuid
    

    def add_domain_to_program(self, program_uuid: str, domain_name: str) -> str:
        """
        Add a domain to a specific Program.
        
        Args:
            program_uuid (str): UUID of the Program
            domain_name (str): Name of the domain to add
        
        Returns:
            str: UUID of the newly created domain
        """
        data = self._read_file()
        
        if program_uuid not in data['programs']:
            raise ProgramManagementError(f"Program with UUID {program_uuid} not found")
        
        # Check if domain name already exists in this Program
        for domain in data['programs'][program_uuid]['domains'].values():
            if domain['domain_name'] == domain_name:
                raise ProgramManagementError(f"Domain '{domain_name}' already exists in this Program")
        
        new_target_uuid = str(uuid.uuid4())
        data['programs'][program_uuid]['domains'][new_target_uuid] = {
            "domain_name": domain_name,
            "commands": {}
        }
        print(f"Debug: Addedd domain '{domain_name}' to Program, with UUID {new_target_uuid}")

        
        self.write_to_file(data)
        return new_target_uuid
    
    def add_command_to_domain(self, target_uuid: str, command_details: Dict[str, Any]) -> None:
        """
        Add a command to a specific domain.
        
        Args:
            target_uuid (str): UUID of the domain
            command_details (Dict): Details of the command to add
        """
        data = self._read_file()
        
        # Find the domain
        domain_found = False
        for Program in data['programs'].values():
            if target_uuid in Program['domains']:
                domain = Program['domains'][target_uuid]
                command_name = command_details.get('command_name', '')
                
                if command_name in domain['commands']: # Chcek if the same command was there in the domain.
                    # raise ProgramManagementError(f"Command '{command_name}' already exists in this domain")
                    pass
                
                domain['commands'][command_name] = command_details
                domain_found = True
                break
            
        if not domain_found:
            return (f"Domain with UUID {target_uuid} not found")
        
        self.write_to_file(data)
        return data

    def get_program_by_uuid(self, program_uuid: str) -> Dict[str, Any]:
        """
        Retrieve a Program by its UUID.
        
        Args:
            program_uuid (str): UUID of the Program
        
        Returns:
            Dict: Program details
        """
        data = self._read_file()
        
        if program_uuid not in data['programs']:
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
        
        for Program in data['programs'].values():
            if target_uuid in Program['domains']:
                return Program['domains'][target_uuid]
        
        raise ProgramManagementError(f"Domain with UUID {target_uuid} not found")
    
    def get_domain_by_name(self, domain_name: str) -> Dict[str, Any]:
        """
        Retrieve a domain by its name.
        
        Args:
            domain_name (str): Name of the domain
        
        Returns:
            Dict: Domain details including its UUID and parent Program UUID
        """
        data = self._read_file()
        
        for program_uuid, Program in data['programs'].items():
            for target_uuid, domain in Program['domains'].items():
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
            Dict: Command details including domain and Program UUIDs
        """
        data = self._read_file()
        
        for program_uuid, Program in data['programs'].items():
            for target_uuid, domain in Program['domains'].items():
                if command_name in domain['commands']:
                    return {
                        "program_uuid": program_uuid,
                        "target_uuid": target_uuid,
                        **domain['commands'][command_name]
                    }
        
        raise ProgramManagementError(f"Command with name {command_name} not found")
    
    def list_programs(self) -> Dict[str, str]:
        """
        List all programs with their UUIDs.
        
        Returns:
            Dict: Mapping of Program UUIDs to Program names
        """
        data = self._read_file()
        return {uuid: Program['program_name'] for uuid, Program in data['programs'].items()}
    
    def list_domains_in_program(self, program_uuid: str) -> Dict[str, str]:
        """
        List all domains in a specific Program.
        
        Args:
            program_uuid (str): UUID of the Program
        
        Returns:
            Dict: Mapping of domain UUIDs to domain names
        """
        Program = self.get_program_by_uuid(program_uuid)
        return {uuid: domain['domain_name'] for uuid, domain in Program['domains'].items()}
    
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

        This method allows you to extract the process IDs (PIDs) for all commands 
        registered in a particular domain. It provides a convenient way to track 
        running processes associated with a specific domain.

        Args:
            target_uuid (str): The unique identifier of the domain to search

        Returns:
            Dict[str, int]: A dictionary where:
                - Keys are command names
                - Values are their corresponding process IDs (PIDs)

        Raises:
            ProgramManagementError: If the domain is not found or has no commands
        """
        try:
            # Retrieve the entire domain details
            domain = self.get_domain_by_uuid(target_uuid)
            
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
                print(f"Warning: No PIDs found for domain UUID {target_uuid}")
            
            return command_pids

        except ProgramManagementError as e:
            print(f"Error retrieving PIDs for domain {target_uuid}: {e}")
            raise



    def update_command_status_by_pid(self, pid: int, new_status: str):
        """
        Update the status of a command based on its Process ID (PID).
        
        This method provides a flexible way to update command status by searching 
        through all programs, domains, and commands to find a matching PID. This is 
        particularly useful in scenarios where you want to track and update the 
        status of a running process across different domains and programs.

        Args:
            pid (int): The Process ID of the command to update
            new_status (str): The new status to set for the command

        Returns:
            Dict[str, Any]: Details of the updated command, including:
                - program_uuid: UUID of the Program containing the command
                - target_uuid: UUID of the domain containing the command
                - command_name: Name of the command that was updated
                - previous_status: Status before the update
                - new_status: Updated status

        Raises:
            ProgramManagementError: If no command with the given PID is found
        """
        # Read the entire file data
        data = self._read_file()
        
        # Iterate through programs, domains, and commands to find matching PID
        for program_uuid, Program in data['programs'].items():
            for target_uuid, domain in Program['domains'].items():
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
                            'program_uuid': program_uuid,
                            'target_uuid': target_uuid,
                            'command_name': command_name,
                            'previous_status': previous_status,
                            'new_status': new_status
                        }
        
        # If no matching PID is found, raise an error
        raise ProgramManagementError(f"No command found with PID {pid}")

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
            including Program and domain information

        Raises:
            ProgramManagementError: If no command with the given PID is found
        """
        data = self._read_file()
        
        for program_uuid, Program in data['programs'].items():
            for target_uuid, domain in Program['domains'].items():
                for command_name, command_details in domain['commands'].items():
                    if command_details.get('pid') == pid:
                        return {
                            'program_uuid': program_uuid,
                            'target_uuid': target_uuid,
                            'command_name': command_name,
                            'command_details': command_details
                        }
        
        raise ProgramManagementError(f"No command found with PID {pid}")








    def get_program_by_name(self, program_name: str) -> Dict[str, Any]:
        """
        Retrieve a Program by its name with extensive error checking.
        
        Args:
            program_name (str): Name of the Program
        
        Returns:
            Dict: Program details including its UUID
        """
        data = self._read_file()
        for uuid, Program in data['programs'].items():
            if Program['program_name'] == program_name:
                result = {"uuid": uuid, **Program}
                return result
        
        return None
    
    def get_program_uuidby_name(self, program_name: str) -> str:
        """
        Get Program UUID by its name with extensive error handling.
        
        Args:
            program_name (str): Name of the Program
        
        Returns:
            str: UUID of the Program
        """
        try:
            Program = self.get_program_by_name(program_name)
            
            if Program is not None:  # Program was found
                uuid = Program.get('uuid')  # Get UUID from the Program
                return uuid
            else:  # No Program found
                return None

        except ProgramManagementError as e:
            print(f"Error retrieving UUID for Program '{program_name}': {e}")
            raise
    
    def debug_print_programs(self):
        """
        Debug method to print all current programs.
        """
        data = self._read_file()
        print("Current programs:")
        for uuid, Program in data['programs'].items():
            print(f"UUID: {uuid}, Name: {Program['program_name']}")

# Example usage with extensive debugging
# manager = ProgramManager('programs.json')

# Ensure the Program exists
# try:
#     program_uuid = manager.create_program("s")
#     print(f"Program UUID: {program_uuid}")

#     # Verify UUID retrieval
#     retrieved_uuid = manager.get_program_uuidby_name("s")
#     print(f"Retrieved UUID: {retrieved_uuid}")

#     # Additional debugging
#     manager.debug_print_programs()

# except ProgramManagementError as e:
#     print(f"An error occurred: {e}")

