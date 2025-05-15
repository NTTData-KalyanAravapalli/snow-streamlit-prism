"""
Database Management page for PRISM application.
"""

import streamlit as st
import snowflake.snowpark.context as snowpark
from config.config import APP_CONFIG, ACTIONS
from utils.snowflake_utils import (
    get_databases,
    log_audit_event,
    get_current_snowflake_user,
    get_current_snowflake_role
)

def create_database():
    st.subheader("Create Database")
    
    with st.form("create_database_form"):
        db_name = st.text_input("Database Name")
        clone_from = st.selectbox(
            "Clone From (Optional)",
            ["None"] + get_databases(),
            help="Select a database to clone from, or None to create an empty database"
        )
        
        submitted = st.form_submit_button("Create Database")
        
        if submitted:
            if not db_name:
                st.error("Please enter a database name")
                return
            
            try:
                session = snowpark.get_active_session()
                
                if clone_from != "None":
                    session.sql(f"CREATE DATABASE {db_name} CLONE {clone_from}").collect()
                    action = "CLONE_DATABASE"
                else:
                    session.sql(f"CREATE DATABASE {db_name}").collect()
                    action = "CREATE_DATABASE"
                
                # Log the event
                log_audit_event(
                    action=action,
                    object_name=db_name,
                    object_type="DATABASE",
                    details=f"Created database {db_name}" + 
                           (f" by cloning {clone_from}" if clone_from != "None" else "")
                )
                
                st.success(f"Successfully created database {db_name}")
                
            except Exception as e:
                st.error(f"Error creating database: {str(e)}")

def delete_database():
    st.subheader("Delete Database")
    
    with st.form("delete_database_form"):
        db_name = st.selectbox(
            "Select Database to Delete",
            get_databases(),
            help="Select the database you want to delete"
        )
        
        confirm = st.checkbox("I understand this action cannot be undone")
        
        submitted = st.form_submit_button("Delete Database")
        
        if submitted:
            if not confirm:
                st.error("Please confirm that you understand this action cannot be undone")
                return
            
            try:
                session = snowpark.get_active_session()
                session.sql(f"DROP DATABASE {db_name}").collect()
                
                # Log the event
                log_audit_event(
                    action="DELETE_DATABASE",
                    object_name=db_name,
                    object_type="DATABASE",
                    details=f"Deleted database {db_name}"
                )
                
                st.success(f"Successfully deleted database {db_name}")
                
            except Exception as e:
                st.error(f"Error deleting database: {str(e)}")

def main():
    st.title("Database Management")
    st.markdown("---")
    
    # Get the current action from the sidebar
    selected_action = st.session_state.get("selected_action_radio")
    
    if selected_action == ACTIONS["CREATE_DATABASE"] or selected_action == ACTIONS["CLONE_DATABASE"]:
        create_database()
    elif selected_action == ACTIONS["DELETE_DATABASE"]:
        delete_database()
    else:
        st.info("Please select a database management action from the sidebar")
    
    # Display current user and role
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.text(f"Current User: {get_current_snowflake_user()}")
    with col2:
        st.text(f"Current Role: {get_current_snowflake_role()}")

if __name__ == "__main__":
    main() 