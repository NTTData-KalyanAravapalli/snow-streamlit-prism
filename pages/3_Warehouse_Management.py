"""
Warehouse Management page for PRISM application.
"""

import streamlit as st
import snowflake.snowpark.context as snowpark
from config.config import APP_CONFIG, ACTIONS, WAREHOUSE_SIZES, WAREHOUSE_FUNCTIONS
from utils.snowflake_utils import (
    log_audit_event,
    get_current_snowflake_user,
    get_current_snowflake_role
)

def create_warehouse():
    st.subheader("Create Warehouse")
    
    with st.form("create_warehouse_form"):
        # Basic Information
        warehouse_name = st.text_input("Warehouse Name")
        warehouse_size = st.selectbox(
            "Warehouse Size",
            WAREHOUSE_SIZES,
            help="Select the size of the warehouse"
        )
        
        # Advanced Settings
        with st.expander("Advanced Settings"):
            auto_suspend = st.number_input(
                "Auto Suspend (seconds)",
                min_value=0,
                max_value=3600,
                value=300,
                help="Number of seconds of inactivity after which the warehouse is automatically suspended"
            )
            
            auto_resume = st.checkbox(
                "Auto Resume",
                value=True,
                help="Automatically resume the warehouse when a query is submitted"
            )
            
            min_cluster_count = st.number_input(
                "Minimum Cluster Count",
                min_value=1,
                max_value=10,
                value=1,
                help="Minimum number of compute clusters for the warehouse"
            )
            
            max_cluster_count = st.number_input(
                "Maximum Cluster Count",
                min_value=1,
                max_value=10,
                value=1,
                help="Maximum number of compute clusters for the warehouse"
            )
            
            scaling_policy = st.selectbox(
                "Scaling Policy",
                ["STANDARD", "ECONOMY"],
                help="Policy that determines when additional clusters are started"
            )
        
        # Warehouse Function
        warehouse_function = st.selectbox(
            "Warehouse Function",
            WAREHOUSE_FUNCTIONS,
            help="Select the primary function of this warehouse"
        )
        
        submitted = st.form_submit_button("Create Warehouse")
        
        if submitted:
            if not warehouse_name:
                st.error("Please enter a warehouse name")
                return
            
            try:
                session = snowpark.get_active_session()
                
                # Build the CREATE WAREHOUSE statement
                create_stmt = f"""
                CREATE WAREHOUSE {warehouse_name}
                WITH
                    WAREHOUSE_SIZE = {warehouse_size}
                    AUTO_SUSPEND = {auto_suspend}
                    AUTO_RESUME = {str(auto_resume).upper()}
                    MIN_CLUSTER_COUNT = {min_cluster_count}
                    MAX_CLUSTER_COUNT = {max_cluster_count}
                    SCALING_POLICY = {scaling_policy}
                """
                
                session.sql(create_stmt).collect()
                
                # Log the event
                log_audit_event(
                    action="CREATE_WAREHOUSE",
                    object_name=warehouse_name,
                    object_type="WAREHOUSE",
                    details=f"Created warehouse {warehouse_name} with size {warehouse_size} and function {warehouse_function}"
                )
                
                st.success(f"Successfully created warehouse {warehouse_name}")
                
            except Exception as e:
                st.error(f"Error creating warehouse: {str(e)}")

def main():
    st.title("Warehouse Management")
    st.markdown("---")
    
    # Get the current action from the sidebar
    selected_action = st.session_state.get("selected_action_radio")
    
    if selected_action == ACTIONS["CREATE_WAREHOUSE"]:
        create_warehouse()
    else:
        st.info("Please select a warehouse management action from the sidebar")
    
    # Display current user and role
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.text(f"Current User: {get_current_snowflake_user()}")
    with col2:
        st.text(f"Current Role: {get_current_snowflake_role()}")

if __name__ == "__main__":
    main() 