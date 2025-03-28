import json

from app.services.monitor_endpoints.db.db_manager import DatabaseManager
from app.services.monitor_endpoints.db.db_operations import DatabaseOperations

db_config = {
    'dbname': 'test_monitor',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost'
}

db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)

def get_review_endpoints():
    result = []
    data = db_ops.query_operations().get_need_review_endpoints()
    if data is not None:
        for row in data:
            result.append({
                'program_uuid': row[0],
                'target_id': row[1],
                'scan_name': row[2],
                'url': row[3],
                'change_detected_at': row[4],  # You may need to convert this to a simpler format if required
                'new_status_code': row[5],
                'old_body_file_path': row[6],
                'new_body_file_path': row[7]
            })

        # Convert the result into JSON format
        json_result = json.dumps(result)
        return json_result
    else:
        return None

print(get_review_endpoints())