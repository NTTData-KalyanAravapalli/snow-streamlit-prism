"""
About page for PRISM application.
"""

import streamlit as st
from config.config import APP_CONFIG

st.title("About PRISM")
st.markdown("---")

st.markdown("""
### What is PRISM?

PRISM (Platform for Role-based Identity and Security Management) is a comprehensive tool designed to streamline and automate the management of Snowflake resources, roles, and permissions. It provides a user-friendly interface for database administrators and security teams to manage their Snowflake environment efficiently.

### Key Features

1. **Database Management**
   - Create new databases
   - Clone existing databases
   - Delete databases
   - Manage database roles and permissions

2. **Warehouse Management**
   - Create and configure warehouses
   - Set up warehouse access controls
   - Monitor warehouse usage

3. **Role Management**
   - Create and manage roles
   - Assign roles to users
   - Manage role hierarchies
   - Configure database-specific roles
   - Create environment-specific roles

4. **Security and Compliance**
   - Role-based access control (RBAC)
   - Audit logging
   - Security policy enforcement
   - Compliance reporting

5. **Cost Analysis**
   - Monitor resource usage
   - Track costs
   - Generate usage reports

### Getting Started

1. Select your account from the sidebar
2. Choose an action from the available options
3. Follow the guided interface to complete your task

### Best Practices

- Always review role assignments before applying changes
- Use the audit logs to track changes
- Follow the principle of least privilege
- Regularly review and update role hierarchies
- Monitor resource usage and costs

### Support

For support or questions, please contact:
- Email: support@prism.com
- Documentation: [PRISM Documentation](https://docs.prism.com)
""")

st.markdown("---")
st.markdown(f"Version: {APP_CONFIG['APP']['VERSION']}") 