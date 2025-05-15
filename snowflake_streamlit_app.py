import streamlit as st
import snowflake.connector
from snowflake.connector import DictCursor
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Snowflake connection parameters
SNOWFLAKE_CONFIG = {
    'account': os.getenv('SNOWFLAKE_ACCOUNT'),
    'user': os.getenv('SNOWFLAKE_USER'),
    'password': os.getenv('SNOWFLAKE_PASSWORD'),
    'role': os.getenv('SNOWFLAKE_ROLE'),
    'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
    'database': os.getenv('SNOWFLAKE_DATABASE')
}

def get_snowflake_connection():
    """Create and return a Snowflake connection"""
    try:
        conn = snowflake.connector.connect(
            **SNOWFLAKE_CONFIG
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to Snowflake: {str(e)}")
        return None

def execute_query(query, params=None):
    """Execute a query and return results as a DataFrame"""
    try:
        conn = get_snowflake_connection()
        if conn:
            with conn.cursor(DictCursor) as cur:
                if params:
                    cur.execute(query, params)
                else:
                    cur.execute(query)
                results = cur.fetchall()
                return pd.DataFrame(results)
    except Exception as e:
        st.error(f"Error executing query: {str(e)}")
    finally:
        if conn:
            conn.close()
    return pd.DataFrame()

def main():
    st.set_page_config(
        page_title="PRISM - Snowflake Management",
        page_icon="❄️",
        layout="wide"
    )

    st.title("PRISM - Snowflake Management Platform")
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select a page:",
            ["Dashboard", "Database Management", "Warehouse Management", "Role Management", "Cost Analysis"]
        )

    if page == "Dashboard":
        show_dashboard()
    elif page == "Database Management":
        show_database_management()
    elif page == "Warehouse Management":
        show_warehouse_management()
    elif page == "Role Management":
        show_role_management()
    elif page == "Cost Analysis":
        show_cost_analysis()

def show_dashboard():
    st.header("Dashboard")
    
    # Get current user and role
    user_query = "SELECT CURRENT_USER() as user, CURRENT_ROLE() as role"
    user_info = execute_query(user_query)
    
    if not user_info.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current User", user_info['USER'].iloc[0])
        with col2:
            st.metric("Current Role", user_info['ROLE'].iloc[0])

    # Get warehouse usage
    warehouse_query = """
    SELECT WAREHOUSE_NAME, 
           CREDITS_USED, 
           CREDITS_USED_COMPUTE, 
           CREDITS_USED_CLOUD_SERVICES
    FROM TABLE(INFORMATION_SCHEMA.WAREHOUSE_METERING_HISTORY(
        DATE_RANGE_START=>DATEADD('days',-7,CURRENT_DATE()),
        DATE_RANGE_END=>CURRENT_DATE()
    ))
    ORDER BY START_TIME DESC
    """
    warehouse_usage = execute_query(warehouse_query)
    
    if not warehouse_usage.empty:
        st.subheader("Warehouse Usage (Last 7 Days)")
        fig = px.bar(warehouse_usage, 
                    x='WAREHOUSE_NAME', 
                    y='CREDITS_USED',
                    title='Warehouse Credit Usage')
        st.plotly_chart(fig, use_container_width=True)

def show_database_management():
    st.header("Database Management")
    
    # List databases
    db_query = "SHOW DATABASES"
    databases = execute_query(db_query)
    
    if not databases.empty:
        st.subheader("Available Databases")
        st.dataframe(databases[['name', 'created_on', 'owner']])

def show_warehouse_management():
    st.header("Warehouse Management")
    
    # List warehouses
    wh_query = "SHOW WAREHOUSES"
    warehouses = execute_query(wh_query)
    
    if not warehouses.empty:
        st.subheader("Available Warehouses")
        st.dataframe(warehouses[['name', 'state', 'type', 'size']])

def show_role_management():
    st.header("Role Management")
    
    # List roles
    role_query = "SHOW ROLES"
    roles = execute_query(role_query)
    
    if not roles.empty:
        st.subheader("Available Roles")
        st.dataframe(roles[['name', 'assigned_to_users', 'granted_to_roles']])

def show_cost_analysis():
    st.header("Cost Analysis")
    
    # Get credit usage by warehouse
    credit_query = """
    SELECT WAREHOUSE_NAME,
           SUM(CREDITS_USED) as TOTAL_CREDITS,
           AVG(CREDITS_USED) as AVG_CREDITS
    FROM TABLE(INFORMATION_SCHEMA.WAREHOUSE_METERING_HISTORY(
        DATE_RANGE_START=>DATEADD('days',-30,CURRENT_DATE()),
        DATE_RANGE_END=>CURRENT_DATE()
    ))
    GROUP BY WAREHOUSE_NAME
    ORDER BY TOTAL_CREDITS DESC
    """
    credit_usage = execute_query(credit_query)
    
    if not credit_usage.empty:
        st.subheader("Credit Usage by Warehouse (Last 30 Days)")
        fig = px.pie(credit_usage, 
                    values='TOTAL_CREDITS', 
                    names='WAREHOUSE_NAME',
                    title='Warehouse Credit Distribution')
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main() 