# PRISM - Snowflake Management Platform

PRISM is a Streamlit-based application for managing Snowflake resources, including databases, warehouses, roles, and more. It provides a user-friendly interface for common Snowflake administrative tasks.

## Features

- Database Management (Create, Clone, Delete)
- Warehouse Management
- Role Management and Hierarchy
- RBAC Architecture Visualization
- Metadata Management
- Cost Analysis
- Audit Logs

## Prerequisites

- Python 3.8+
- Snowflake account and credentials
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/PRISM.git
cd PRISM
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your Snowflake credentials:
```
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ROLE=your_role
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
```

## Running the Application

1. Activate the virtual environment (if not already activated):
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Run the Streamlit application:
```bash
streamlit run Home.py
```

The application will be available at `http://localhost:8501`

## Project Structure

```
PRISM/
├── Home.py                 # Main application file
├── pages/                  # Application pages
├── config/                 # Configuration files
├── utils/                  # Utility functions
├── requirements.txt        # Project dependencies
└── README.md              # Project documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Kalyan Aravapalli
