"""
Audit Logs page for PRISM application.
"""

import streamlit as st
import snowflake.snowpark.context as snowpark
import pandas as pd
from datetime import datetime, timedelta
from config.config import APP_CONFIG, ACTIONS
from utils.snowflake_utils import (
    get_current_snowflake_user,
    get_current_snowflake_role
)

def view_audit_logs():
    st.subheader("Audit Logs")
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=30),
            help="Select the start date for audit logs"
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            help="Select the end date for audit logs"
        )
    
    # Filter options
    col3, col4 = st.columns(2)
    with col3:
        action_filter = st.multiselect(
            "Filter by Action",
            ["CREATE_DATABASE", "CLONE_DATABASE", "DELETE_DATABASE", "CREATE_WAREHOUSE",
             "CREATE_ROLE", "ASSIGN_ROLES", "ASSIGN_DATABASE_ROLES", "REVOKE_ROLES",
             "CREATE_ENVIRONMENT_ROLES", "MANAGE_METADATA"],
            help="Select actions to filter by"
        )
    with col4:
        object_type_filter = st.multiselect(
            "Filter by Object Type",
            ["DATABASE", "WAREHOUSE", "ROLE"],
            help="Select object types to filter by"
        )
    
    try:
        session = snowpark.get_active_session()
        
        # Build the query
        query = f"""
        SELECT 
            EVENT_ID,
            EVENT_TIMESTAMP,
            ACTION,
            OBJECT_NAME,
            OBJECT_TYPE,
            USER_NAME,
            ROLE_NAME,
            DETAILS
        FROM {APP_CONFIG['DB']['NAME']}.{APP_CONFIG['DB']['SCHEMA']}.{APP_CONFIG['TABLES']['AUDIT_LOG']}
        WHERE EVENT_TIMESTAMP >= '{start_date}'
        AND EVENT_TIMESTAMP <= '{end_date}'
        """
        
        # Add filters if selected
        if action_filter:
            actions_str = "', '".join(action_filter)
            query += f" AND ACTION IN ('{actions_str}')"
        
        if object_type_filter:
            types_str = "', '".join(object_type_filter)
            query += f" AND OBJECT_TYPE IN ('{types_str}')"
        
        query += " ORDER BY EVENT_TIMESTAMP DESC"
        
        # Execute query
        logs_df = session.sql(query).to_pandas()
        
        if not logs_df.empty:
            # Display the logs
            st.dataframe(logs_df)
            
            # Download option
            csv = logs_df.to_csv(index=False)
            st.download_button(
                label="Download Audit Logs",
                data=csv,
                file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            # Summary statistics
            st.markdown("### Summary Statistics")
            
            # Actions summary
            st.markdown("#### Actions Summary")
            action_summary = logs_df['ACTION'].value_counts()
            st.bar_chart(action_summary)
            
            # Object types summary
            st.markdown("#### Object Types Summary")
            type_summary = logs_df['OBJECT_TYPE'].value_counts()
            st.bar_chart(type_summary)
            
            # User activity summary
            st.markdown("#### User Activity Summary")
            user_summary = logs_df['USER_NAME'].value_counts()
            st.bar_chart(user_summary)
            
        else:
            st.info("No audit logs found for the selected filters")
            
    except Exception as e:
        st.error(f"Error viewing audit logs: {str(e)}")

def main():
    st.title("Audit Logs")
    st.markdown("---")
    
    # Get the current action from the sidebar
    selected_action = st.session_state.get("selected_action_radio")
    
    if selected_action == ACTIONS["AUDIT_LOGS"]:
        view_audit_logs()
    else:
        st.info("Please select an audit logs action from the sidebar")
    
    # Display current user and role
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.text(f"Current User: {get_current_snowflake_user()}")
    with col2:
        st.text(f"Current Role: {get_current_snowflake_role()}")

if __name__ == "__main__":
    main() 