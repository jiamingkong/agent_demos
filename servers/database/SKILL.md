---
name: database
description: Database operations for SQLite, PostgreSQL, and MySQL (requires appropriate drivers).
allowed-tools:
  - connect_sqlite
  - execute_sql
  - fetch_rows
  - create_table
  - list_tables
  - disconnect
---

# Database Skill

This skill enables the agent to interact with SQL databases.

## Tools

### connect_sqlite
Connect to a SQLite database file (creates if doesn't exist).
- `db_path`: Path to the SQLite database file.

### execute_sql
Execute a SQL statement (SELECT, INSERT, UPDATE, DELETE, etc.).
- `connection_id`: Identifier of the active connection (returned by connect_sqlite).
- `sql`: SQL statement to execute.
- `parameters`: Optional parameters for parameterized query (list/dict).

### fetch_rows
Fetch rows from a SELECT query result (must call execute_sql first).
- `connection_id`: Identifier of the active connection.
- `limit`: Maximum number of rows to fetch (optional, default=100).

### create_table
Create a new table with specified columns.
- `connection_id`: Identifier of the active connection.
- `table_name`: Name of the table to create.
- `columns`: List of column definitions, e.g., ["id INTEGER PRIMARY KEY", "name TEXT", "age INTEGER"].

### list_tables
List all tables in the database.
- `connection_id`: Identifier of the active connection.

### disconnect
Close a database connection.
- `connection_id`: Identifier of the active connection.
