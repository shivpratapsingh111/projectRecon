# db_queries.py
class QueryManager:
    """Centralized query management"""

    # Table creation queries
    CREATE_ENDPOINTS_TABLE = """
        CREATE TABLE IF NOT EXISTS endpoints (
            id SERIAL PRIMARY KEY,
            url TEXT UNIQUE NOT NULL,
            last_check TIMESTAMP,
            last_status_code INTEGER,
            last_response_size INTEGER,
            last_body_hash TEXT,
            last_response_body TEXT,
            last_headers JSONB,
            response_time FLOAT
        )
    """

    CREATE_CHANGES_TABLE = """
        CREATE TABLE IF NOT EXISTS changes (
            id SERIAL PRIMARY KEY,
            endpoint_id INTEGER REFERENCES endpoints(id),
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            old_status_code INTEGER,
            new_status_code INTEGER,
            old_size INTEGER,
            new_size INTEGER,
            old_body_hash TEXT,
            new_body_hash TEXT,
            old_response_body TEXT,
            new_response_body TEXT,
            old_headers JSONB,
            new_headers JSONB,
            old_response_time FLOAT,
            new_response_time FLOAT,
            change_type TEXT[]
        )
    """

    # Insert queries
    INSERT_ENDPOINT = """
        INSERT INTO endpoints (url) VALUES (%s) RETURNING id
    """

    INSERT_CHANGE = """
        INSERT INTO changes (
            endpoint_id, old_status_code, new_status_code,
            old_size, new_size, old_body_hash, new_body_hash, old_response_body, new_response_body, old_headers, new_headers, old_response_time, new_response_time, change_type
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # Select queries
    SELECT_ENDPOINT_DATA = """
        SELECT last_status_code, last_response_size, last_body_hash, last_response_body, last_headers, response_time, id 
        FROM endpoints WHERE url = %s
    """

    SELECT_ALL_ENDPOINTS = """
        SELECT id, url FROM endpoints
    """

    # Update queries
    UPDATE_ENDPOINT_DATA = """
        UPDATE endpoints SET
            last_check = CURRENT_TIMESTAMP,
            last_status_code = %s,
            last_response_size = %s,
            last_body_hash = %s,
            last_response_body = %s,
            last_headers = %s,
            response_time = %s
        WHERE id = %s
    """

    # Delete queries
    DELETE_ENDPOINT = """
        DELETE FROM endpoints WHERE id = %s
    """

    DELETE_CHANGES_FOR_ENDPOINT = """
        DELETE FROM changes WHERE endpoint_id = %s
    """
