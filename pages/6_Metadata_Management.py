"""
Metadata Management page for PRISM application.
"""

import streamlit as st
import snowflake.snowpark.context as snowpark
import pandas as pd
from config.config import APP_CONFIG, ACTIONS, ROLE_TYPES
from utils.snowflake_utils import (
    get_all_roles,
    get_function_names,
    log_audit_event,
    get_current_snowflake_user,
    get_current_snowflake_role
)

def manage_metadata():
    st.subheader("Manage Role Metadata")
    
    # Get all roles
    roles = get_all_roles()
    
    if not roles:
        st.warning("No roles found in the system")
        return
    
    # Create tabs for different metadata management functions
    tab1, tab2 = st.tabs(["Update Role Metadata", "View Role Metadata"])
    
    with tab1:
        st.markdown("### Update Role Metadata")
        
        with st.form("update_metadata_form"):
            # Role selection
            role = st.selectbox(
                "Select Role",
                roles,
                help="Select the role to update metadata for"
            )
            
            # Role type
            role_type = st.selectbox(
                "Role Type",
                list(ROLE_TYPES.keys()),
                help="Select the type of role"
            )
            
            # Function selection for functional roles
            if role_type == "FUNCTIONAL":
                functions = get_function_names(role_type)
                selected_functions = st.multiselect(
                    "Select Functions",
                    functions,
                    help="Select the functions this role will have access to"
                )
            
            # Description
            description = st.text_area(
                "Description",
                help="Enter a description for the role"
            )
            
            # Owner
            owner = st.text_input(
                "Owner",
                help="Enter the owner of the role"
            )
            
            submitted = st.form_submit_button("Update Metadata")
            
            if submitted:
                try:
                    session = snowpark.get_active_session()
                    
                    # Update role metadata in the metadata table
                    update_stmt = f"""
                    MERGE INTO {APP_CONFIG['DB']['NAME']}.{APP_CONFIG['DB']['SCHEMA']}.{APP_CONFIG['TABLES']['ROLE_METADATA']}
                    USING (SELECT '{role}' as ROLE_NAME) as source
                    ON {APP_CONFIG['TABLES']['ROLE_METADATA']}.ROLE_NAME = source.ROLE_NAME
                    WHEN MATCHED THEN
                        UPDATE SET
                            ROLE_TYPE = '{role_type}',
                            DESCRIPTION = '{description}',
                            OWNER = '{owner}',
                            UPDATED_AT = CURRENT_TIMESTAMP()
                    WHEN NOT MATCHED THEN
                        INSERT (ROLE_NAME, ROLE_TYPE, DESCRIPTION, OWNER, CREATED_AT, UPDATED_AT)
                        VALUES ('{role}', '{role_type}', '{description}', '{owner}', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
                    """
                    
                    session.sql(update_stmt).collect()
                    
                    # Log the event
                    log_audit_event(
                        action="MANAGE_METADATA",
                        object_name=role,
                        object_type="ROLE",
                        details=f"Updated metadata for role {role}"
                    )
                    
                    st.success(f"Successfully updated metadata for role {role}")
                    
                except Exception as e:
                    st.error(f"Error updating metadata: {str(e)}")
    
    with tab2:
        st.markdown("### View Role Metadata")
        
        try:
            session = snowpark.get_active_session()
            
            # Query the metadata table
            query = f"""
            SELECT 
                ROLE_NAME,
                ROLE_TYPE,
                DESCRIPTION,
                OWNER,
                CREATED_AT,
                UPDATED_AT
            FROM {APP_CONFIG['DB']['NAME']}.{APP_CONFIG['DB']['SCHEMA']}.{APP_CONFIG['TABLES']['ROLE_METADATA']}
            ORDER BY ROLE_NAME
            """
            
            metadata_df = session.sql(query).to_pandas()
            
            if not metadata_df.empty:
                st.dataframe(metadata_df)
            else:
                st.info("No role metadata found")
                
        except Exception as e:
            st.error(f"Error viewing metadata: {str(e)}")

def main():
    st.title("Metadata Management")
    st.markdown("---")
    
    # Get the current action from the sidebar
    selected_action = st.session_state.get("selected_action_radio")
    
    if selected_action == ACTIONS["MANAGE_METADATA"]:
        manage_metadata()
    else:
        st.info("Please select a metadata management action from the sidebar")
    
    # Display current user and role
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.text(f"Current User: {get_current_snowflake_user()}")
    with col2:
        st.text(f"Current Role: {get_current_snowflake_role()}")

if __name__ == "__main__":
    main() 