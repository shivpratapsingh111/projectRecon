import json  
from app.interface.json_data_manager import GroupManager
group_manager = GroupManager()

def remove_domain_by_id(group_id: str, domain_id: str):
    """
    Remove a domain and all its associated commands from a group.

    Args:
        group_id (str): UUID of the group containing the domain
        domain_id (str): UUID of the domain to remove

    Returns:
        Dict: Details of the removed domain
    """
    data = group_manager._read_file()

    if group_id in data["groups"]:
        group = data["groups"][group_id]
        if domain_id in group["domains"]:
            removed_domain = group["domains"].pop(domain_id)  # Remove domain
            
            group_manager._write_to_file(data)  # Save updated data
            
            return {
                "group_id": group_id,
                "removed_domain_id": domain_id,
                "removed_domain_name": removed_domain.get("domain_name", "Unknown"),
                "message": "Domain removed successfully"
            }



    
    
# update_group_status_by_id("4d2cb9e2-f2fd-4968-8398-30293f87d5a0", "running")
remove_domain_by_id("4d2cb9e2-f2fd-4968-8398-30293f87d5a0", "8b81b181-a243-48a8-a36e-34b00319609f")
