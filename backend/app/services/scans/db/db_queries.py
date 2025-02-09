# db_queries.py
class QueryManager:
    """Centralized query management"""

    SELECT_ALL_PROGRAMNAMES = """
        SELECT program_name FROM programs 
    """
