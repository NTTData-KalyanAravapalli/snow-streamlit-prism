"""
Configuration settings for PRISM application.
"""

# Application Configuration
APP_CONFIG = {
    "APP": {
        "TITLE": "Portal for Role Integration, Security & Management",
        "LOGO_URL": "NTT-Data-Logo.png"
    },
    "DATABASE": {
        "NAME": "SECURITY",
        "SCHEMA": "ACCESS_CONTROL"
    },
    "TABLES": {
        "ENVIRONMENTS": "ENVIRONMENTS",
        "ROLE_METADATA": "FUNCTIONAL_TECHNICAL_ROLE_METADATA",
        "AUDIT_LOG": "AUDIT_LOG",
        "AUDIT_LOG_SEQUENCE": "SEQ_AUDIT_LOG",
        "ROLE_HIERARCHY_LOG": "ROLE_HIERARCHY_LOG",
        "ROLE_HIERARCHY_LOG_SEQUENCE": "SEQ_ROLE_HIERARCHY_LOG"
    },
    "STORED_PROCEDURES": {
        "DATABASE_CONTROLLER": "SP_DATABASE_CONTROLLER",
        "ENVIRONMENT_ROLE_CONTROLLER": "SP_ENVIRONMENT_ROLE_CONTROLLER",
        "MANAGE_FUNCTIONAL_TECHNICAL_ROLES": "SP_MANAGE_FUNCTIONAL_TECHNICAL_ROLES_CONTROLLER"
    }
}

# Action Constants
ACTIONS = {
    "ABOUT": "About PRISM",
    "CREATE_DATABASE": "Create a Database",
    "CLONE_DATABASE": "Clone a Database",
    "DELETE_DATABASE": "Delete a Database",
    "CREATE_WAREHOUSE": "Create a Warehouse",
    "CREATE_ROLE": "Create a Role",
    "ASSIGN_ROLES": "Assign Roles",
    "ASSIGN_DATABASE_ROLES": "Assign Database Roles",
    "REVOKE_ROLES": "Revoke Roles",
    "CREATE_ENVIRONMENT_ROLES": "Create Environment Roles",
    "SHOW_ROLE_HIERARCHY": "Show Role Hierarchy",
    "DISPLAY_RBAC_ARCHITECTURE": "Display RBAC Architecture",
    "MANAGE_METADATA": "Manage Metadata",
    "COST_ANALYSIS": "Cost Analysis",
    "AUDIT_LOGS": "Audit Logs"
}

# Role Types
ROLE_TYPES = {
    "FUNCTIONAL": "Functional",
    "TECHNICAL": "Technical"
}

# Access Level Mapping
ACCESS_LEVEL_MAP = {
    "Read-Only (e.g., SELECT on tables)": "RO_AR",
    "Read-Write (e.g., SELECT, INSERT, UPDATE, DELETE)": "RW_AR",
    "Full Access (e.g., ALL PRIVILEGES on objects)": "FULL_AR",
    "DB Admin (e.g., OWNERSHIP or MANAGE GRANTS on DB)": "DBA_AR"
}

# Warehouse Sizes
WAREHOUSE_SIZES = [
    "XSMALL", "SMALL", "MEDIUM", "LARGE", 
    "XLARGE", "XXLARGE", "XXXLARGE"
]

# Warehouse Functions
WAREHOUSE_FUNCTIONS = [
    "GEN", "ETL", "DATALOADER", "ANALYTICS", 
    "BI_TOOL", "CUSTOM"
]

# Helper function to get fully qualified object names
def get_fully_qualified_name(object_name, include_db=True):
    """
    Generate fully qualified name for database objects.
    Args:
        object_name: The name of the table/sequence/procedure
        include_db: Whether to include database name in the path
    Returns:
        Fully qualified name (e.g., "DATABASE.SCHEMA.OBJECT" or "SCHEMA.OBJECT")
    """
    if include_db:
        return f"{APP_CONFIG['DATABASE']['NAME']}.{APP_CONFIG['DATABASE']['SCHEMA']}.{object_name}"
    return f"{APP_CONFIG['DATABASE']['SCHEMA']}.{object_name}" 