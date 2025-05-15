"""
Role Management page for PRISM application.
"""

import streamlit as st
import snowflake.snowpark.context as snowpark
from config.config import APP_CONFIG, ACTIONS, ROLE_TYPES, ACCESS_LEVEL_MAP
from utils.snowflake_utils import (
    get_all_roles,
    get_function_names,
    get_databases,
    log_audit_event,
    log_role_hierarchy_event,
    get_current_snowflake_user,
    get_current_snowflake_role
)

def create_role():
    st.subheader("Create Role")
    
    with st.form("create_role_form"):
        role_name = st.text_input("Role Name")
        role_type = st.selectbox(
            "Role Type",
            list(ROLE_TYPES.keys()),
            help="Select the type of role to create"
        )
        
        # For functional roles, show function selection
        if role_type == "FUNCTIONAL":
            functions = get_function_names(role_type)
            selected_functions = st.multiselect(
                "Select Functions",
                functions,
                help="Select the functions this role will have access to"
            )
        
        submitted = st.form_submit_button("Create Role")
        
        if submitted:
            if not role_name:
                st.error("Please enter a role name")
                return
            
            try:
                session = snowpark.get_active_session()
                session.sql(f"CREATE ROLE {role_name}").collect()
                
                # Log the event
                log_audit_event(
                    action="CREATE_ROLE",
                    object_name=role_name,
                    object_type="ROLE",
                    details=f"Created {role_type.lower()} role {role_name}"
                )
                
                st.success(f"Successfully created role {role_name}")
                
            except Exception as e:
                st.error(f"Error creating role: {str(e)}")

def assign_roles():
    st.subheader("Assign Roles")
    
    with st.form("assign_roles_form"):
        target_role = st.selectbox(
            "Target Role",
            get_all_roles(),
            help="Select the role to assign privileges to"
        )
        
        roles_to_assign = st.multiselect(
            "Roles to Assign",
            get_all_roles(),
            help="Select the roles to assign to the target role"
        )
        
        submitted = st.form_submit_button("Assign Roles")
        
        if submitted:
            if not roles_to_assign:
                st.error("Please select at least one role to assign")
                return
            
            try:
                session = snowpark.get_active_session()
                
                for role in roles_to_assign:
                    session.sql(f"GRANT ROLE {role} TO ROLE {target_role}").collect()
                    
                    # Log the event
                    log_role_hierarchy_event(
                        parent_role=target_role,
                        child_role=role,
                        action="GRANT"
                    )
                
                st.success(f"Successfully assigned roles to {target_role}")
                
            except Exception as e:
                st.error(f"Error assigning roles: {str(e)}")

def assign_database_roles():
    st.subheader("Assign Database Roles")
    
    with st.form("assign_database_roles_form"):
        database = st.selectbox(
            "Database",
            get_databases(),
            help="Select the database to assign roles for"
        )
        
        target_role = st.selectbox(
            "Target Role",
            get_all_roles(),
            help="Select the role to assign database privileges to"
        )
        
        access_level = st.selectbox(
            "Access Level",
            list(ACCESS_LEVEL_MAP.keys()),
            help="Select the level of access to grant"
        )
        
        submitted = st.form_submit_button("Assign Database Role")
        
        if submitted:
            try:
                session = snowpark.get_active_session()
                
                # Grant the appropriate privileges based on access level
                access_code = ACCESS_LEVEL_MAP[access_level]
                session.sql(f"GRANT {access_code} ON DATABASE {database} TO ROLE {target_role}").collect()
                
                # Log the event
                log_audit_event(
                    action="ASSIGN_DATABASE_ROLES",
                    object_name=database,
                    object_type="DATABASE",
                    details=f"Granted {access_level} access on {database} to role {target_role}"
                )
                
                st.success(f"Successfully assigned {access_level} access on {database} to {target_role}")
                
            except Exception as e:
                st.error(f"Error assigning database role: {str(e)}")

def revoke_roles():
    st.subheader("Revoke Roles")
    
    with st.form("revoke_roles_form"):
        target_role = st.selectbox(
            "Target Role",
            get_all_roles(),
            help="Select the role to revoke privileges from"
        )
        
        roles_to_revoke = st.multiselect(
            "Roles to Revoke",
            get_all_roles(),
            help="Select the roles to revoke from the target role"
        )
        
        submitted = st.form_submit_button("Revoke Roles")
        
        if submitted:
            if not roles_to_revoke:
                st.error("Please select at least one role to revoke")
                return
            
            try:
                session = snowpark.get_active_session()
                
                for role in roles_to_revoke:
                    session.sql(f"REVOKE ROLE {role} FROM ROLE {target_role}").collect()
                    
                    # Log the event
                    log_role_hierarchy_event(
                        parent_role=target_role,
                        child_role=role,
                        action="REVOKE"
                    )
                
                st.success(f"Successfully revoked roles from {target_role}")
                
            except Exception as e:
                st.error(f"Error revoking roles: {str(e)}")

def create_environment_roles():
    st.subheader("Create Environment Roles")
    
    with st.form("create_environment_roles_form"):
        environment = st.text_input("Environment Name")
        base_role = st.selectbox(
            "Base Role",
            get_all_roles(),
            help="Select the base role to create environment-specific roles from"
        )
        
        submitted = st.form_submit_button("Create Environment Roles")
        
        if submitted:
            if not environment:
                st.error("Please enter an environment name")
                return
            
            try:
                session = snowpark.get_active_session()
                
                # Create environment-specific role
                env_role = f"{base_role}_{environment}"
                session.sql(f"CREATE ROLE {env_role}").collect()
                session.sql(f"GRANT ROLE {base_role} TO ROLE {env_role}").collect()
                
                # Log the event
                log_audit_event(
                    action="CREATE_ENVIRONMENT_ROLES",
                    object_name=env_role,
                    object_type="ROLE",
                    details=f"Created environment-specific role {env_role} based on {base_role}"
                )
                
                st.success(f"Successfully created environment role {env_role}")
                
            except Exception as e:
                st.error(f"Error creating environment role: {str(e)}")

def main():
    st.title("Role Management")
    st.markdown("---")
    
    # Get the current action from the sidebar
    selected_action = st.session_state.get("selected_action_radio")
    
    if selected_action == ACTIONS["CREATE_ROLE"]:
        create_role()
    elif selected_action == ACTIONS["ASSIGN_ROLES"]:
        assign_roles()
    elif selected_action == ACTIONS["ASSIGN_DATABASE_ROLES"]:
        assign_database_roles()
    elif selected_action == ACTIONS["REVOKE_ROLES"]:
        revoke_roles()
    elif selected_action == ACTIONS["CREATE_ENVIRONMENT_ROLES"]:
        create_environment_roles()
    else:
        st.info("Please select a role management action from the sidebar")
    
    # Display current user and role
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.text(f"Current User: {get_current_snowflake_user()}")
    with col2:
        st.text(f"Current Role: {get_current_snowflake_role()}")

if __name__ == "__main__":
    main() 