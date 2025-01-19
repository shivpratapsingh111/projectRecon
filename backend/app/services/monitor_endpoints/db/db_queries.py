# db_queries.py
class QueryManager:
    """Centralized query management"""

# Table creation queries

    # --- Endpoint Monitor ---
    CREATE_ENDPOINTS_TABLE = """
        CREATE TABLE IF NOT EXISTS monitor_endpoints (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
            target_id UUID REFERENCES web_targets(id) ON DELETE CASCADE,
            scan_name TEXT,
            scan_interval INTEGER DEFAULT 4,
            status TEXT DEFAULT 'active',
            url TEXT UNIQUE NOT NULL,
            old_status_code INTEGER,
            new_status_code INTEGER,
            old_response_size TEXT,
            new_response_size TEXT,
            old_body_hash TEXT,
            new_body_hash TEXT,
            old_body_file_path TEXT,
            new_body_file_path TEXT,
            change_detected_at TEXT,
            need_review BOOLEAN DEFAULT FALSE,
            last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    
    CREATE_TABLE_LIST = [CREATE_ENDPOINTS_TABLE]
# ---

# Insert queries

    # --- Endpoint Monitor ---
    INSERT_ENDPOINT = """
        INSERT INTO monitor_endpoints (
            program_id, target_id, scan_name, status, url, old_status_code, new_status_code, old_response_size, new_response_size, old_body_hash, new_body_hash, old_body_file_path, new_body_file_path, change_detected_at, need_review, last_check
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
    """

# ---

# Select queries

    # --- Endpoint Monitor ---
    SELECT_ENDPOINT_DATA_BY_URL = """
        SELECT id, program_id, target_id, scan_name, url, old_status_code, new_status_code,
            old_response_size, new_response_size, old_body_hash, new_body_hash, old_body_file_path, new_body_file_path, change_detected_at, need_review, last_check
        FROM monitor_endpoints WHERE url = %s
    """
    SELECT_ENDPOINT_DATA_BY_ID = """
        SELECT id, program_id, target_id, scan_name, url, old_status_code, new_status_code,
            old_response_size, new_response_size, old_body_hash, new_body_hash, old_body_file_path, new_body_file_path, change_detected_at, need_review, last_check
        FROM monitor_endpoints WHERE id = %s
    """
    SELECT_ALL_ENDPOINTS = """
        SELECT id, program_id, scan_name, url FROM monitor_endpoints
    """
    SELECT_ALL_PROGRAMS = """
        SELECT * FROM programs
    """
    GET_NEED_REVIEW_ENDPOINTS = """
        SELECT
            id,
            program_id,
            target_id, 
            scan_name, 
            url,
            change_detected_at, 
            old_status_code,
            new_status_code, 
            old_response_size, 
            new_response_size, 
            old_body_file_path, 
            new_body_file_path 
        FROM monitor_endpoints 
        WHERE need_review = TRUE
    """
    GET_ENDPOINT_RESPONSE_BODY_FILEPATHS = """
        SELECT
            old_body_file_path,
            new_body_file_path 
        FROM monitor_endpoints 
        WHERE id = %s
    """
    GET_TARGET_AND_PROGRAM_ID = """
        SELECT
            id,
            program_id
        FROM web_targets 
        WHERE target_domain = %s
    """
    GET_ENDPOINTS_DATA_BY_STATUS = """
        SELECT
            id,
            program_id,
            scan_name,
            scan_interval,
            status,
            url,
            new_status_code,
            new_response_size,
            new_body_file_path,
            last_check
        FROM monitor_endpoints 
        WHERE status = %s
    """
    GET_PROGRAM_NAME = """
        SELECT 
            program_name
        FROM programs
        WHERE id = %s
    """
# ---

# Update queries

    # --- Endpoint Monitor ---
    UPDATE_ENDPOINT_DATA = """
        UPDATE monitor_endpoints SET
            old_status_code = %s,
            new_status_code = %s,
            old_response_size = %s,
            new_response_size = %s,
            old_body_hash = %s,
            new_body_hash = %s,
            old_body_file_path = %s,
            new_body_file_path = %s,
            change_detected_at = %s,
            need_review = %s,
            last_check = CURRENT_TIMESTAMP
        WHERE id = %s
    """
    UPDATE_ENDPOINT_TIMESTAMP = """
        UPDATE monitor_endpoints
            SET last_check = CURRENT_TIMESTAMP
            WHERE id = %s
    """
    UPDATE_NEED_REVIEW_ENDPOINT = """
        UPDATE monitor_endpoints
            SET need_review = FALSE
        WHERE id = %s
    """
    UPDATE_ENDPOINT_STATUS = """
        UPDATE monitor_endpoints
            SET status = %s
        WHERE id = %s
    """
    UPDATE_ENDPOINT_SCAN_INTERVAL = """
        UPDATE monitor_endpoints
            SET scan_interval = %s
        WHERE id = %s
    """
    
# ---

# Delete queries

    # --- Endpoint Monitor ---
    DELETE_ENDPOINT = """
        DELETE FROM monitor_endpoints WHERE id = %s
    """