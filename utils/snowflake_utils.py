"""
Utility functions for Snowflake operations.
"""

import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
from datetime import datetime, timedelta
from config.config import APP_CONFIG, get_fully_qualified_name

# Initialize Snowflake session
try:
    session = get_active_session()
    if session is None:
        st.error("Failed to get active Snowpark session. Ensure you are running this in a Snowflake-connected environment.")
        st.stop()
except Exception as e:
    st.error(f"Error establishing Snowflake session: {e}")
    st.stop()

@st.cache_data(ttl=600)
def get_environments():
    """Fetches available environment names from the ENVIRONMENTS_TABLE."""
    try:
        env_df = session.table(get_fully_qualified_name(APP_CONFIG["TABLES"]["ENVIRONMENTS"])).select("ENVIRONMENT_NAME").distinct()
        return sorted([row["ENVIRONMENT_NAME"] for row in env_df.collect()])
    except Exception as e:
        st.error(f"Error fetching environments: {e}")
        return []

@st.cache_data(ttl=600)
def get_function_names(role_type_filter: str):
    """Fetches function names based on role type from ROLE_METADATA_TABLE."""
    try:
        role_df = session.table(get_fully_qualified_name(APP_CONFIG["TABLES"]["ROLE_METADATA"])).filter(f"ROLE_TYPE = '{role_type_filter}'").select("FUNCTION_NAME").distinct()
        return sorted([row["FUNCTION_NAME"] for row in role_df.collect()])
    except Exception as e:
        st.error(f"Error fetching function names: {e}")
        return []

@st.cache_data(ttl=300)
def get_databases():
    """Fetches all database names in the current account."""
    try:
        dbs = session.sql("SHOW DATABASES").collect()
        return sorted([db["name"] for db in dbs if db["name"]])
    except Exception as e:
        st.error(f"Error fetching databases: {e}")
        return []

@st.cache_data(ttl=300)
def get_all_roles():
    """Fetches all role names in the current account."""
    try:
        roles_df = session.sql("SHOW ROLES").collect()
        return sorted([role["name"] for role in roles_df if role["name"]])
    except Exception as e:
        st.error(f"Error fetching roles: {e}")
        return []

def get_current_snowflake_user() -> str:
    """Gets the current Snowflake user."""
    try:
        return session.sql("SELECT CURRENT_USER()").collect()[0][0]
    except Exception:
        return "UNKNOWN_USER"

def get_current_snowflake_role() -> str:
    """Safely get the current role from the session."""
    try:
        return session.sql("SELECT CURRENT_ROLE()").collect()[0][0]
    except Exception:
        return "UNKNOWN_ROLE"

def log_audit_event(
    event_type: str,
    object_name: str,
    sql_command: str,
    status: str,
    message: str = "",
    invoked_by_role: str = None,
    invoked_by_user: str = None,
) -> int:
    """Logs an audit event to the AUDIT_LOG_TABLE and returns the event_id."""
    if invoked_by_role is None:
        invoked_by_role = get_current_snowflake_role()
    if invoked_by_user is None:
        invoked_by_user = get_current_snowflake_user()

    event_id = None
    try:
        event_id_result = session.sql(f"SELECT {get_fully_qualified_name(APP_CONFIG['TABLES']['AUDIT_LOG_SEQUENCE'])}.NEXTVAL AS ID").collect()
        if not event_id_result:
            st.warning(f"Audit logging failed for '{event_type}': Could not retrieve next event ID from sequence.")
            return None
        event_id = event_id_result[0]["ID"]

        insert_sql = f"""
            INSERT INTO {get_fully_qualified_name(APP_CONFIG['TABLES']['AUDIT_LOG'])} (
                EVENT_ID, EVENT_TIME, INVOKED_BY, INVOKED_BY_ROLE, EVENT_TYPE,
                OBJECT_NAME, SQL_COMMAND, STATUS, MESSAGE
            ) VALUES (
                {event_id}, CURRENT_TIMESTAMP(), '{invoked_by_user}', '{invoked_by_role}',
                '{event_type}', '{object_name}', $${sql_command}$$, '{status}', $${message}$$
            )
        """
        session.sql(insert_sql).collect()
        return event_id
    except Exception as e:
        return event_id

def log_role_hierarchy_event(
    audit_event_id: int,
    invoked_by: str,
    environment_name: str,
    created_role_name: str,
    created_role_type: str,
    mapped_database_role: str,
    parent_account_role: str,
    sql_command_create_role: str,
    sql_command_grant_db_role: str,
    sql_command_grant_ownership: str,
    status: str,
    message: str = "",
):
    """Logs an event to the ROLE_HIERARCHY_LOG table."""
    try:
        log_id_result = session.sql(f"SELECT {get_fully_qualified_name(APP_CONFIG['TABLES']['ROLE_HIERARCHY_LOG_SEQUENCE'])}.NEXTVAL AS ID").collect()
        if not log_id_result:
            st.warning(f"Role hierarchy logging failed for '{created_role_name}': Could not retrieve LOG_ID from sequence.")
            return
        log_id = log_id_result[0]["ID"]

        insert_sql = f"""
            INSERT INTO {get_fully_qualified_name(APP_CONFIG['TABLES']['ROLE_HIERARCHY_LOG'])} (
                LOG_ID, EVENT_TIME, AUDIT_EVENT_ID, INVOKED_BY, ENVIRONMENT_NAME,
                CREATED_ROLE_NAME, CREATED_ROLE_TYPE, MAPPED_DATABASE_ROLE,
                PARENT_ACCOUNT_ROLE, SQL_COMMAND_CREATE_ROLE, SQL_COMMAND_GRANT_DB_ROLE,
                SQL_COMMAND_GRANT_OWNERSHIP, STATUS, MESSAGE
            ) VALUES (
                {log_id}, CURRENT_TIMESTAMP(), {audit_event_id if audit_event_id else "NULL"},
                '{invoked_by}', '{environment_name}', '{created_role_name}',
                '{created_role_type}', '{mapped_database_role}', '{parent_account_role}',
                $${sql_command_create_role}$$, $${sql_command_grant_db_role}$$,
                $${sql_command_grant_ownership}$$, '{status}', $${message}$$
            )
        """
        session.sql(insert_sql).collect()
    except Exception as e:
        return audit_event_id

@st.cache_data(ttl=300)
def get_current_role_grants(role_name):
    """Fetch current grants for a specific role."""
    try:
        query = f"""
        SELECT 
            NAME as GRANTED_ROLE,
            GRANTEE_NAME as GRANTED_TO_ROLE,
            CREATED_ON as GRANT_DATE
        FROM SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_ROLES
        WHERE GRANTEE_NAME = '{role_name}'
            AND PRIVILEGE = 'USAGE'
            AND GRANTED_ON = 'ROLE'
            AND DELETED_ON IS NULL
        ORDER BY CREATED_ON DESC
        """
        return session.sql(query).to_pandas()
    except Exception as e:
        st.error(f"Error fetching role grants: {e}")
        return pd.DataFrame(columns=['GRANTED_ROLE', 'GRANTED_TO_ROLE', 'GRANT_DATE'])

@st.cache_data(ttl=300)
def get_functional_technical_roles():
    """Fetch all roles with _FR or _TR suffix."""
    try:
        query = """
        SELECT DISTINCT name as ROLE_NAME
        FROM SNOWFLAKE.ACCOUNT_USAGE.ROLES
        WHERE (name LIKE '%_FR' OR name LIKE '%_TR')
        AND DELETED_ON IS NULL
        ORDER BY name
        """
        return session.sql(query).to_pandas()
    except Exception as e:
        st.error(f"Error fetching roles: {e}")
        return pd.DataFrame(columns=['ROLE_NAME']) 