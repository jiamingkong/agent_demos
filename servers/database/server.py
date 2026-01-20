from mcp.server.fastmcp import FastMCP
import sqlite3
import uuid
import json

mcp = FastMCP("database", log_level="ERROR")

# In-memory store for database connections
_connections = {}

def _get_connection(connection_id: str):
    """Retrieve a connection by ID, raise error if not found."""
    if connection_id not in _connections:
        raise ValueError(f"Connection {connection_id} not found.")
    return _connections[connection_id]

@mcp.tool()
def connect_sqlite(db_path: str) -> str:
    """
    Connect to a SQLite database file (creates if doesn't exist).

    Args:
        db_path: Path to the SQLite database file.
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # to get dict-like rows
        connection_id = str(uuid.uuid4())[:8]
        _connections[connection_id] = {
            "conn": conn,
            "cursor": None,
            "last_result": None
        }
        return f"Connected to SQLite database at {db_path}. Connection ID: {connection_id}"
    except Exception as e:
        return f"Error connecting to database: {e}"

@mcp.tool()
def execute_sql(connection_id: str, sql: str, parameters: str = None) -> str:
    """
    Execute a SQL statement (SELECT, INSERT, UPDATE, DELETE, etc.).

    Args:
        connection_id: Identifier of the active connection (returned by connect_sqlite).
        sql: SQL statement to execute.
        parameters: Optional parameters for parameterized query (JSON string of list/dict).
    """
    try:
        conn_data = _get_connection(connection_id)
        conn = conn_data["conn"]
        cursor = conn.cursor()
        # Parse parameters if provided
        params = None
        if parameters:
            try:
                params = json.loads(parameters)
                if isinstance(params, dict):
                    params = tuple(params.values())
                elif isinstance(params, list):
                    params = tuple(params)
            except json.JSONDecodeError:
                return "Error: parameters must be valid JSON."
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        conn.commit()
        # Store cursor and result
        conn_data["cursor"] = cursor
        conn_data["last_result"] = cursor.description  # column info for SELECT
        if sql.strip().upper().startswith("SELECT"):
            rowcount = len(cursor.fetchall())
            cursor.execute(sql)  # re-execute? better to store result.
            # Instead, we'll fetch later.
            return f"SELECT executed successfully. Use fetch_rows to retrieve rows."
        else:
            return f"SQL executed successfully. Rows affected: {cursor.rowcount}"
    except Exception as e:
        return f"Error executing SQL: {e}"

@mcp.tool()
def fetch_rows(connection_id: str, limit: int = 100) -> str:
    """
    Fetch rows from a SELECT query result (must call execute_sql first).

    Args:
        connection_id: Identifier of the active connection.
        limit: Maximum number of rows to fetch (optional, default=100).
    """
    try:
        conn_data = _get_connection(connection_id)
        cursor = conn_data["cursor"]
        if cursor is None:
            return "Error: No previous SELECT query executed. Use execute_sql with SELECT first."
        rows = cursor.fetchmany(limit)
        if not rows:
            return "No more rows to fetch."
        # Convert rows to list of dicts
        columns = [col[0] for col in cursor.description] if cursor.description else []
        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error fetching rows: {e}"

@mcp.tool()
def create_table(connection_id: str, table_name: str, columns: list) -> str:
    """
    Create a new table with specified columns.

    Args:
        connection_id: Identifier of the active connection.
        table_name: Name of the table to create.
        columns: List of column definitions, e.g., ["id INTEGER PRIMARY KEY", "name TEXT", "age INTEGER"].
    """
    if not columns:
        return "Error: columns list cannot be empty."
    columns_sql = ", ".join(columns)
    sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
    return execute_sql(connection_id, sql)

@mcp.tool()
def list_tables(connection_id: str) -> str:
    """
    List all tables in the database.

    Args:
        connection_id: Identifier of the active connection.
    """
    sql = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    result = execute_sql(connection_id, sql)
    if "Error" in result:
        return result
    # fetch rows
    return fetch_rows(connection_id, limit=100)

@mcp.tool()
def disconnect(connection_id: str) -> str:
    """
    Close a database connection.

    Args:
        connection_id: Identifier of the active connection.
    """
    try:
        conn_data = _get_connection(connection_id)
        conn_data["conn"].close()
        del _connections[connection_id]
        return f"Connection {connection_id} closed."
    except Exception as e:
        return f"Error disconnecting: {e}"

if __name__ == "__main__":
    mcp.run()
