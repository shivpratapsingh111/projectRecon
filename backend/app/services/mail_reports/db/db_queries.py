# db_queries.py
class QueryManager:
    """Centralized query management for Send Reports Feature"""

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
    
    
    CREATE_TABLE_LIST = [CREATE_PROGRAMS_TABLE, CREATE_WEB_TARGETS_TABLE, CREATE_MOBILE_TARGETS_TABLE]

# ---

# Insert queries

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

    # --- Report ---
    UPDATE_MOBILE_TARGET_DATA = """
    UPDATE mobile_targets
        SET vulnerability_reported = ARRAY_APPEND(COALESCE(vulnerability_reported, '{}'), %s)
    WHERE id = %s
"""


# ---

# Delete queries

