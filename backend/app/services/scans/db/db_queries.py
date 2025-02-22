# db_queries.py
class QueryManager:
    """Centralized query management"""

    SELECT_ALL_PROGRAMNAMES = """
        SELECT program_name FROM programs 
    """
    INSERT_WEB_TARGETS = """
        INSERT INTO web_targets (program_id, target_domain) 
        VALUES (%s, %s) 
        ON CONFLICT (target_domain) DO NOTHING
    """
    GET_WEB_TARGET_ID = """
        SELECT 
            id
        FROM web_targets
        WHERE target_domain = %s
    """
