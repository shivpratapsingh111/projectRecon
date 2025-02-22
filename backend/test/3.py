import json  
from app.interface.json_data_manager import GroupManager
group_manager = GroupManager()

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
    
    
    
update_execution_status("c06506a6-0d22-49be-acaf-2dc3833c78b6", "93b587a8-8ed6-4e33-bc5d-62a65108cfa5")
