# from app.services.monitor_endpoints.db.db_manager import DatabaseManager
# from app.services.monitor_endpoints.db.db_operations import DatabaseOperations
import os, json, uuid
import psycopg2
from psycopg2.extras import execute_values

# from app.db.db_queries import QueryManager
# db_query = QueryManager

db_config = {
    'dbname': 'test_monitor',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost'
}

# db_manager = DatabaseManager(db_config)
# db_ops = DatabaseOperations(db_manager)

def read_jsonl_file(file_path):
    with open(file_path, "r") as file:
        return [json.loads(line) for line in file]

UPDATE_WEB_TARGETS_DATA = """
    UPDATE web_targets SET
        technology = %s,
        status_code = %s,
        port = %s,
        host = %s,
        ipv4 = %s,
        ipv6 = %s,
        response_time = %s,
        webserver = %s
    WHERE target_domain = %s;
"""


def update_subdomains_to_db(db_config):
    file_path = "/home/retro/projectRecon-Data/latest-cyber/thecyberboy.com/subdomains/httpx_subdomains.json"
    
    if os.path.exists(file_path):
        subdomains_data = read_jsonl_file(file_path)
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                for entry in subdomains_data:
                    values = (
                        entry.get("tech", []),  # Keep as a list for PostgreSQL array
                        entry.get("status_code"),
                        entry.get("port"),
                        entry.get("host"),
                        entry.get("a", []),  # Keep as a list
                        entry.get("aaaa", []),
                        entry.get("time"),
                        entry.get("webserver"),
                        entry.get("input")
                    )
                    cursor.execute(UPDATE_WEB_TARGETS_DATA, values)
                
                conn.commit()
    else:
        print("Doesn't Exists")
update_subdomains_to_db(db_config)