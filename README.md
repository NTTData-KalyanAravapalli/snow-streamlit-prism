# PRISM - Platform for Role-based Identity and Security Management

PRISM is a comprehensive tool designed to streamline and automate the management of Snowflake resources, roles, and permissions. It provides a user-friendly interface for database administrators and security teams to manage their Snowflake environment efficiently.

## Features

- **Database Management**
  - Create new databases
  - Clone existing databases
  - Delete databases
  - Manage database roles and permissions

- **Warehouse Management**
  - Create and configure warehouses
  - Set up warehouse access controls
  - Monitor warehouse usage

- **Role Management**
  - Create and manage roles
  - Assign roles to users
  - Manage role hierarchies
  - Configure database-specific roles
  - Create environment-specific roles

- **Security and Compliance**
  - Role-based access control (RBAC)
  - Audit logging
  - Security policy enforcement
  - Compliance reporting

- **Cost Analysis**
  - Monitor resource usage
  - Track costs
  - Generate usage reports

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/prism.git
   cd prism
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your Snowflake credentials:
   ```
   SNOWFLAKE_ACCOUNT=your_account
   SNOWFLAKE_USER=your_username
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_ROLE=your_role
   SNOWFLAKE_WAREHOUSE=your_warehouse
   SNOWFLAKE_DATABASE=your_database
   SNOWFLAKE_SCHEMA=your_schema
   ```

5. Run the application:
   ```bash
   streamlit run Home.py
   ```

## Usage

1. Select your account from the sidebar
2. Choose an action from the available options
3. Follow the guided interface to complete your task

## Best Practices

- Always review role assignments before applying changes
- Use the audit logs to track changes
- Follow the principle of least privilege
- Regularly review and update role hierarchies
- Monitor resource usage and costs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support or questions, please contact:
- Email: support@prism.com
- Documentation: [PRISM Documentation](https://docs.prism.com)
