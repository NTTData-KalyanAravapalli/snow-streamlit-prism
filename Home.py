"""
Main application file for PRISM.
"""

import streamlit as st
from config.config import APP_CONFIG, ACTIONS
from utils.snowflake_utils import (
    get_current_snowflake_user,
    get_current_snowflake_role
)

def main():
    # Set page configuration
    st.set_page_config(
        page_title=APP_CONFIG["APP"]["TITLE"],
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for dark/light mode
    st.markdown("""
        <style>
        /* Light mode styles */
        [data-testid="stAppViewContainer"] {
            background-color: #f0f9ff;
        }
        [data-testid="stSidebar"] {
            background-color: #29e5e8;
        }
        .sidebar-content {
            color: white;
        }
        
        /* Dark mode styles */
        @media (prefers-color-scheme: dark) {
            [data-testid="stAppViewContainer"] {
                background-color: #1E1E1E;
            }
            [data-testid="stSidebar"] {
                background-color: #2C2C2C;
            }
            .stMarkdown, .stText {
                color: #FFFFFF !important;
            }
            .stMetric {
                background-color: #363636 !important;
                color: #FFFFFF !important;
            }
            /* Plotly charts in dark mode */
            .js-plotly-plot .plotly {
                background-color: #2C2C2C !important;
            }
            .js-plotly-plot .plotly .main-svg {
                background-color: #2C2C2C !important;
            }
            /* Dataframes/tables in dark mode */
            .stDataFrame {
                background-color: #363636 !important;
                color: #FFFFFF !important;
            }
            /* Select boxes and inputs */
            .stSelectbox, .stTextInput, .stDateInput {
                background-color: #363636 !important;
                color: #FFFFFF !important;
            }
            /* Buttons */
            .stButton button {
                background-color: #4A4A4A !important;
                color: #FFFFFF !important;
            }
            /* Tabs */
            .stTab {
                background-color: #363636 !important;
                color: #FFFFFF !important;
            }
            /* Expander */
            .streamlit-expanderHeader {
                background-color: #363636 !important;
                color: #FFFFFF !important;
            }
            /* Tab content */
            .stTabContent {
                background-color: #2C2C2C !important;
                color: #FFFFFF !important;
            }
            /* Multiselect */
            .stMultiSelect {
                background-color: #363636 !important;
                color: #FFFFFF !important;
            }
            /* Date input */
            .stDateInput > div {
                background-color: #363636 !important;
                color: #FFFFFF !important;
            }
            /* Links */
            a {
                color: #00CED1 !important;
            }
            /* Headers */
            h1, h2, h3, h4, h5, h6 {
                color: #FFFFFF !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image(APP_CONFIG["APP"]["LOGO_URL"], width=500)
        st.image("Prism Designer.jpeg", width=500)
        
        # Account Context
        st.markdown("### Account Context")
        available_accounts = ["PRIMARY", "SECONDARY", "SANDBOX"]
        selected_account = st.selectbox(
            "Select Account:",
            available_accounts,
            key="selected_account",
        )
       
        # Session Information
        st.markdown("### Current Session")
        current_user = get_current_snowflake_user()
        current_role = get_current_snowflake_role()
       
        session_container = st.container()
        with session_container:
            user_col1, user_col2 = st.columns([1, 2])
            with user_col1:
                st.text("User:")
            with user_col2:
                st.text(current_user)
           
            role_col1, role_col2 = st.columns([1, 2])
            with role_col1:
                st.text("Role:")
            with role_col2:
                st.text(current_role)
       
        st.markdown("---")
       
        # Actions section
        st.markdown("### Actions")
        selected_action = st.radio(
            "",
            list(ACTIONS.values()),
            key="selected_action_radio"
        )
       
        # Footer information
        st.markdown("---")
        st.markdown("### App Information")
       
        info_container = st.container()
        with info_container:
            ver_col1, ver_col2 = st.columns([1, 2])
            with ver_col1:
                st.text("Version:")
            with ver_col2:
                st.text("1.0.0")
           
            auth_col1, auth_col2 = st.columns([1, 2])
            with auth_col1:
                st.text("Author:")
            with auth_col2:
                st.text("Kalyan Aravapalli")

    # Main content area
    st.title(APP_CONFIG["APP"]["TITLE"])
    st.markdown("---")
   
    # Action Dispatcher
    if selected_action == ACTIONS["ABOUT"]:
        st.switch_page("pages/1_About.py")
    elif selected_action == ACTIONS["CREATE_DATABASE"]:
        st.switch_page("pages/2_Database_Management.py")
    elif selected_action == ACTIONS["CLONE_DATABASE"]:
        st.switch_page("pages/2_Database_Management.py")
    elif selected_action == ACTIONS["DELETE_DATABASE"]:
        st.switch_page("pages/2_Database_Management.py")
    elif selected_action == ACTIONS["CREATE_WAREHOUSE"]:
        st.switch_page("pages/3_Warehouse_Management.py")
    elif selected_action == ACTIONS["CREATE_ROLE"]:
        st.switch_page("pages/4_Role_Management.py")
    elif selected_action == ACTIONS["ASSIGN_ROLES"]:
        st.switch_page("pages/4_Role_Management.py")
    elif selected_action == ACTIONS["ASSIGN_DATABASE_ROLES"]:
        st.switch_page("pages/4_Role_Management.py")
    elif selected_action == ACTIONS["REVOKE_ROLES"]:
        st.switch_page("pages/4_Role_Management.py")
    elif selected_action == ACTIONS["CREATE_ENVIRONMENT_ROLES"]:
        st.switch_page("pages/4_Role_Management.py")
    elif selected_action == ACTIONS["SHOW_ROLE_HIERARCHY"]:
        st.switch_page("pages/5_Role_Hierarchy.py")
    elif selected_action == ACTIONS["DISPLAY_RBAC_ARCHITECTURE"]:
        st.switch_page("pages/5_Role_Hierarchy.py")
    elif selected_action == ACTIONS["MANAGE_METADATA"]:
        st.switch_page("pages/6_Metadata_Management.py")
    elif selected_action == ACTIONS["COST_ANALYSIS"]:
        st.switch_page("pages/7_Cost_Analysis.py")
    elif selected_action == ACTIONS["AUDIT_LOGS"]:
        st.switch_page("pages/8_Audit_Logs.py")
    else:
        st.info("Select an action from the sidebar to get started.")

if __name__ == "__main__":
    main()
