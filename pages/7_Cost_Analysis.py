"""
Cost Analysis page for PRISM application.
"""

import streamlit as st
import snowflake.snowpark.context as snowpark
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from config.config import APP_CONFIG, ACTIONS
from utils.snowflake_utils import (
    get_current_snowflake_user,
    get_current_snowflake_role
)

def analyze_costs():
    st.subheader("Cost Analysis")
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=30),
            help="Select the start date for cost analysis"
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            help="Select the end date for cost analysis"
        )
    
    # Analysis type selection
    analysis_type = st.selectbox(
        "Analysis Type",
        ["Warehouse Usage", "Database Storage", "Query Costs"],
        help="Select the type of cost analysis to perform"
    )
    
    try:
        session = snowpark.get_active_session()
        
        if analysis_type == "Warehouse Usage":
            # Query warehouse usage
            query = f"""
            SELECT 
                WAREHOUSE_NAME,
                DATE_TRUNC('HOUR', START_TIME) as HOUR,
                SUM(CREDITS_USED) as CREDITS_USED,
                SUM(CREDITS_USED_COMPUTE) as COMPUTE_CREDITS,
                SUM(CREDITS_USED_CLOUD_SERVICES) as CLOUD_SERVICES_CREDITS
            FROM {APP_CONFIG['DB']['NAME']}.{APP_CONFIG['DB']['SCHEMA']}.WAREHOUSE_METERING_HISTORY
            WHERE START_TIME >= '{start_date}'
            AND START_TIME <= '{end_date}'
            GROUP BY WAREHOUSE_NAME, HOUR
            ORDER BY HOUR DESC
            """
            
            usage_df = session.sql(query).to_pandas()
            
            if not usage_df.empty:
                # Create time series plot
                fig = px.line(
                    usage_df,
                    x='HOUR',
                    y='CREDITS_USED',
                    color='WAREHOUSE_NAME',
                    title='Warehouse Credit Usage Over Time'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Display summary statistics
                st.markdown("### Summary Statistics")
                summary_df = usage_df.groupby('WAREHOUSE_NAME').agg({
                    'CREDITS_USED': 'sum',
                    'COMPUTE_CREDITS': 'sum',
                    'CLOUD_SERVICES_CREDITS': 'sum'
                }).reset_index()
                
                st.dataframe(summary_df)
            else:
                st.info("No warehouse usage data found for the selected period")
        
        elif analysis_type == "Database Storage":
            # Query database storage
            query = f"""
            SELECT 
                DATABASE_NAME,
                DATE_TRUNC('DAY', USAGE_DATE) as DAY,
                SUM(STORAGE_BYTES) as STORAGE_BYTES,
                SUM(FAILSAFE_BYTES) as FAILSAFE_BYTES
            FROM {APP_CONFIG['DB']['NAME']}.{APP_CONFIG['DB']['SCHEMA']}.DATABASE_STORAGE_USAGE_HISTORY
            WHERE USAGE_DATE >= '{start_date}'
            AND USAGE_DATE <= '{end_date}'
            GROUP BY DATABASE_NAME, DAY
            ORDER BY DAY DESC
            """
            
            storage_df = session.sql(query).to_pandas()
            
            if not storage_df.empty:
                # Convert bytes to GB
                storage_df['STORAGE_GB'] = storage_df['STORAGE_BYTES'] / (1024**3)
                storage_df['FAILSAFE_GB'] = storage_df['FAILSAFE_BYTES'] / (1024**3)
                
                # Create time series plot
                fig = px.line(
                    storage_df,
                    x='DAY',
                    y=['STORAGE_GB', 'FAILSAFE_GB'],
                    color='DATABASE_NAME',
                    title='Database Storage Usage Over Time'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Display summary statistics
                st.markdown("### Summary Statistics")
                summary_df = storage_df.groupby('DATABASE_NAME').agg({
                    'STORAGE_GB': 'mean',
                    'FAILSAFE_GB': 'mean'
                }).reset_index()
                
                st.dataframe(summary_df)
            else:
                st.info("No database storage data found for the selected period")
        
        elif analysis_type == "Query Costs":
            # Query query costs
            query = f"""
            SELECT 
                WAREHOUSE_NAME,
                DATE_TRUNC('HOUR', START_TIME) as HOUR,
                COUNT(*) as QUERY_COUNT,
                SUM(TOTAL_ELAPSED_TIME) as TOTAL_ELAPSED_TIME,
                AVG(TOTAL_ELAPSED_TIME) as AVG_ELAPSED_TIME,
                SUM(CREDITS_USED) as CREDITS_USED
            FROM {APP_CONFIG['DB']['NAME']}.{APP_CONFIG['DB']['SCHEMA']}.QUERY_HISTORY
            WHERE START_TIME >= '{start_date}'
            AND START_TIME <= '{end_date}'
            GROUP BY WAREHOUSE_NAME, HOUR
            ORDER BY HOUR DESC
            """
            
            query_df = session.sql(query).to_pandas()
            
            if not query_df.empty:
                # Create time series plot
                fig = px.line(
                    query_df,
                    x='HOUR',
                    y=['QUERY_COUNT', 'CREDITS_USED'],
                    color='WAREHOUSE_NAME',
                    title='Query Count and Credit Usage Over Time'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Display summary statistics
                st.markdown("### Summary Statistics")
                summary_df = query_df.groupby('WAREHOUSE_NAME').agg({
                    'QUERY_COUNT': 'sum',
                    'TOTAL_ELAPSED_TIME': 'sum',
                    'AVG_ELAPSED_TIME': 'mean',
                    'CREDITS_USED': 'sum'
                }).reset_index()
                
                st.dataframe(summary_df)
            else:
                st.info("No query cost data found for the selected period")
                
    except Exception as e:
        st.error(f"Error performing cost analysis: {str(e)}")

def main():
    st.title("Cost Analysis")
    st.markdown("---")
    
    # Get the current action from the sidebar
    selected_action = st.session_state.get("selected_action_radio")
    
    if selected_action == ACTIONS["COST_ANALYSIS"]:
        analyze_costs()
    else:
        st.info("Please select a cost analysis action from the sidebar")
    
    # Display current user and role
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.text(f"Current User: {get_current_snowflake_user()}")
    with col2:
        st.text(f"Current Role: {get_current_snowflake_role()}")

if __name__ == "__main__":
    main() 