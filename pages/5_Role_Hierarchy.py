"""
Role Hierarchy page for PRISM application.
"""

import streamlit as st
import snowflake.snowpark.context as snowpark
import pandas as pd
import plotly.graph_objects as go
from config.config import APP_CONFIG, ACTIONS
from utils.snowflake_utils import (
    get_all_roles,
    get_current_role_grants,
    get_functional_technical_roles,
    get_current_snowflake_user,
    get_current_snowflake_role
)

def build_role_hierarchy():
    """Build a complete role hierarchy graph."""
    roles = get_all_roles()
    hierarchy = {}
    
    for role in roles:
        grants = get_current_role_grants(role)
        if not grants.empty:
            hierarchy[role] = grants['GRANTED_TO'].tolist()
        else:
            hierarchy[role] = []
    
    return hierarchy

def create_hierarchy_plot(hierarchy):
    """Create a Plotly figure for the role hierarchy."""
    # Create nodes and edges
    nodes = []
    edges = []
    
    # Add all roles as nodes
    for role in hierarchy.keys():
        nodes.append(role)
    
    # Add edges for role grants
    for role, grants in hierarchy.items():
        for granted_role in grants:
            edges.append((role, granted_role))
    
    # Create the figure
    fig = go.Figure()
    
    # Add edges
    for edge in edges:
        fig.add_trace(go.Scatter(
            x=[nodes.index(edge[0]), nodes.index(edge[1])],
            y=[0, 1],
            mode='lines',
            line=dict(color='#888', width=1),
            hoverinfo='none'
        ))
    
    # Add nodes
    fig.add_trace(go.Scatter(
        x=[nodes.index(node) for node in nodes],
        y=[0] * len(nodes),
        mode='markers+text',
        marker=dict(
            size=20,
            color='#29e5e8',
            line=dict(color='#888', width=1)
        ),
        text=nodes,
        textposition="top center",
        hoverinfo='text'
    ))
    
    # Update layout
    fig.update_layout(
        title='Role Hierarchy',
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600
    )
    
    return fig

def show_role_hierarchy():
    st.subheader("Role Hierarchy")
    
    try:
        # Build and display the hierarchy
        hierarchy = build_role_hierarchy()
        fig = create_hierarchy_plot(hierarchy)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display the hierarchy as a table
        st.subheader("Role Grants")
        grants_data = []
        for role, grants in hierarchy.items():
            for granted_role in grants:
                grants_data.append({
                    'Parent Role': role,
                    'Child Role': granted_role
                })
        
        if grants_data:
            grants_df = pd.DataFrame(grants_data)
            st.dataframe(grants_df)
        else:
            st.info("No role grants found")
            
    except Exception as e:
        st.error(f"Error displaying role hierarchy: {str(e)}")

def display_rbac_architecture():
    st.subheader("RBAC Architecture")
    
    try:
        # Get functional and technical roles
        roles_df = get_functional_technical_roles()
        
        if not roles_df.empty:
            # Display functional roles
            st.markdown("### Functional Roles")
            functional_roles = roles_df[roles_df['ROLE_TYPE'] == 'FUNCTIONAL']
            if not functional_roles.empty:
                st.dataframe(functional_roles)
            else:
                st.info("No functional roles found")
            
            # Display technical roles
            st.markdown("### Technical Roles")
            technical_roles = roles_df[roles_df['ROLE_TYPE'] == 'TECHNICAL']
            if not technical_roles.empty:
                st.dataframe(technical_roles)
            else:
                st.info("No technical roles found")
            
            # Display role relationships
            st.markdown("### Role Relationships")
            relationships = roles_df[['ROLE_NAME', 'PARENT_ROLE']].dropna()
            if not relationships.empty:
                st.dataframe(relationships)
            else:
                st.info("No role relationships found")
        else:
            st.info("No roles found in the system")
            
    except Exception as e:
        st.error(f"Error displaying RBAC architecture: {str(e)}")

def main():
    st.title("Role Hierarchy")
    st.markdown("---")
    
    # Get the current action from the sidebar
    selected_action = st.session_state.get("selected_action_radio")
    
    if selected_action == ACTIONS["SHOW_ROLE_HIERARCHY"]:
        show_role_hierarchy()
    elif selected_action == ACTIONS["DISPLAY_RBAC_ARCHITECTURE"]:
        display_rbac_architecture()
    else:
        st.info("Please select a role hierarchy action from the sidebar")
    
    # Display current user and role
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.text(f"Current User: {get_current_snowflake_user()}")
    with col2:
        st.text(f"Current Role: {get_current_snowflake_role()}")

if __name__ == "__main__":
    main() 