import json  
from app.interface.json_data_manager import ProgramManager
program_manager = ProgramManager()

def remove_domain_by_id(program_uuid: str, target_uuid: str):
    """
    Remove a domain and all its associated commands from a program.

    Args:
        program_uuid (str): UUID of the program containing the domain
        target_uuid (str): UUID of the domain to remove

    Returns:
        Dict: Details of the removed domain
    """
    data = program_manager._read_file()

    if program_uuid in data["programs"]:
        program = data["programs"][program_uuid]
        if target_uuid in program["domains"]:
            removed_domain = program["domains"].pop(target_uuid)  # Remove domain
            
            program_manager._write_to_file(data)  # Save updated data
            
            return {
                "program_uuid": program_uuid,
                "removed_target_uuid": target_uuid,
                "removed_domain_name": removed_domain.get("domain_name", "Unknown"),
                "message": "Domain removed successfully"
            }



    
    
# update_program_status_by_id("4d2cb9e2-f2fd-4968-8398-30293f87d5a0", "running")
remove_domain_by_id("4d2cb9e2-f2fd-4968-8398-30293f87d5a0", "8b81b181-a243-48a8-a36e-34b00319609f")
