# db_queries.py
class QueryManager:
    """Centralized query management"""

# Table creation queries

    # --- Report ---
    CREATE_PROGRAMS_TABLE = """
        CREATE TABLE IF NOT EXISTS programs (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            program_name TEXT UNIQUE NOT NULL,
            program_url TEXT,
            acquisitions TEXT[],
            email TEXT,
            report_form TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    CREATE_WEB_TARGETS_TABLE = """
        CREATE TABLE IF NOT EXISTS web_targets (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            program_uuid UUID REFERENCES programs(id) ON DELETE CASCADE,
            target_domain TEXT UNIQUE NOT NULL,
            technology TEXT[],
            status_code INTEGER,
            port INTEGER,
            host INET,
            ipv4 TEXT[],
            ipv6 TEXT[],
            response_time TEXT,
            webserver TEXT,
            vulnerability_reported TEXT[],
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    CREATE_MOBILE_TARGETS_TABLE = """
        CREATE TABLE IF NOT EXISTS mobile_targets (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            program_uuid UUID REFERENCES programs(id) ON DELETE CASCADE,
            target_package TEXT UNIQUE NOT NULL,
            target_apk TEXT NOT NULL,
            technology TEXT[],
            download_url TEXT,
            vulnerability_reported TEXT[],
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

    # --- Endpoint Monitor ---
    CREATE_ENDPOINTS_TABLE = """
        CREATE TABLE IF NOT EXISTS monitor_endpoints (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            program_uuid UUID REFERENCES programs(id) ON DELETE CASCADE,
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

    
    CREATE_TABLE_LIST = [CREATE_PROGRAMS_TABLE, CREATE_WEB_TARGETS_TABLE, CREATE_MOBILE_TARGETS_TABLE, CREATE_ENDPOINTS_TABLE]

# ---

# Insert queries

    # --- Endpoint Monitor ---
    INSERT_ENDPOINT = """
        INSERT INTO monitor_endpoints (
            program_uuid, target_id, scan_name, scan_interval, status, url, old_status_code, new_status_code, old_response_size, new_response_size, old_body_hash, new_body_hash, old_body_file_path, new_body_file_path, change_detected_at, need_review, last_check
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
    """

    # --- Report ---
    INSERT_PROGRAM = """
        INSERT INTO programs (program_name, program_url, acquisitions, email, report_form, created_at)
        VALUES (%s, %s,%s, %s, %s, CURRENT_TIMESTAMP) RETURNING id
    """
    INSERT_WEB_TARGET = """
        INSERT INTO web_targets (program_uuid, target_domain, technology, status_code, port, host, ipv4, ipv6, response_time, webserver, vulnerability_reported, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP) RETURNING id
    """
    INSERT_MOBILE_TARGET = """
        INSERT INTO mobile_targets (program_uuid, target_package, target_apk, technology, download_url, vulnerability_reported, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP) RETURNING id
    """
    INSERT_WEB_REPORT = """
        INSERT INTO web_reports (target_id, target_domain, vulnerability_reported, attachment_url, created_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
    """
    INSERT_MOBILE_REPORT = """
        INSERT INTO mobile_reports (target_id, target_package, target_apk, vulnerability_reported, attachment_url, created_at)
            VALUES (%s, %s, %s,  %s, %s, CURRENT_TIMESTAMP)
    """

# ---

# Select queries

    # --- Endpoint Monitor ---
    SELECT_ENDPOINT_DATA_BY_URL = """
        SELECT id, program_uuid, target_id, scan_name, url, old_status_code, new_status_code,
            old_response_size, new_response_size, old_body_hash, new_body_hash, old_body_file_path, new_body_file_path, change_detected_at, need_review, last_check
        FROM monitor_endpoints WHERE url = %s
    """
    SELECT_ENDPOINT_DATA_BY_ID = """
        SELECT id, program_uuid, target_id, scan_name, url, old_status_code, new_status_code,
            old_response_size, new_response_size, old_body_hash, new_body_hash, old_body_file_path, new_body_file_path, change_detected_at, need_review, last_check
        FROM monitor_endpoints WHERE id = %s
    """
    SELECT_ALL_ENDPOINTS = """
        SELECT id, program_uuid, scan_name, url FROM monitor_endpoints
    """
    GET_NEED_REVIEW_ENDPOINTS = """
        SELECT
            id,
            program_uuid,
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
    GET_TARGET_AND_program_uuid = """
        SELECT
            id,
            program_uuid
        FROM web_targets 
        WHERE target_domain = %s
    """
    GET_ENDPOINTS_DATA_BY_STATUS = """
        SELECT
            id,
            program_uuid,
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
    
    # --- Report ---
    GET_PROGRAM_DATA_BY_ID = """
        SELECT * FROM programs WHERE id = %s
    """    
    GET_PROGRAM_DATA_BY_NAME = """
        SELECT * FROM programs WHERE program_name ILIKE %s
    """   
    GET_PROGRAM_DATA_BY_ID = """
        SELECT * FROM programs WHERE id = %s
    """
    GET_WEB_TARGET_BY_ID = """
        SELECT * FROM web_targets WHERE id = %s
    """
    GET_MOBILE_TARGET_BY_ID = """
        SELECT * FROM mobile_targets WHERE id = %s
    """
    GET_MOBILE_TARGET_BY_NAME = """
        SELECT * FROM mobile_targets WHERE target_package ILIKE %s
    """
    CHECK_PROGRAM_EXISTS = """
        SELECT EXISTS (SELECT 1 FROM programs WHERE program_name ILIKE %s)
    """
    CHECK_MOBILE_TARGET_EXISTS = """
        SELECT EXISTS (SELECT 1 FROM mobile_targets WHERE target_package ILIKE %s)
    """
    CHECK_WEB_TARGET_EXISTS = """
        SELECT EXISTS (SELECT 1 FROM web_targets WHERE target_domain ILIKE %s)
    """
    CHECK_MOBILE_TARGET_VULN_EXISTS = """
    SELECT %s = ANY(vulnerability_reported) 
    FROM mobile_targets 
    WHERE target_package ILIKE %s
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
            WHERE id = %s;
    """
    UPDATE_NEED_REVIEW_ENDPOINT = """
        UPDATE monitor_endpoints
            SET need_review = FALSE
        WHERE id = %s;
    """
    
    # --- Report ---
    UPDATE_MOBILE_TARGET_DATA = """
    UPDATE mobile_targets
        SET vulnerability_reported = ARRAY_APPEND(COALESCE(vulnerability_reported, '{}'), %s)
    WHERE id = %s
"""


# ---

# Delete queries

    # --- Endpoint Monitor ---
    DELETE_ENDPOINT = """
        DELETE FROM monitor_endpoints WHERE id = %s
    """