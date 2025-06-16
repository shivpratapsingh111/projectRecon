# Internal imports
from app.db.db_manager import DatabaseManager
from app.config.db_config import DB_CONFIG
from app.db.db_operations import DatabaseOperations

# Initialization
db_manager = DatabaseManager(DB_CONFIG)
db_ops = DatabaseOperations(db_manager)