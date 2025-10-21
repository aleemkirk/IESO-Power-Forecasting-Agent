"""
PostgreSQL Client for IESO Data

This module provides a clean interface for connecting to and querying the
IESO electricity demand data stored in PostgreSQL (Neon).

Author: IESO Forecasting Agent
Date: 2025-10-21
"""

import os
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
import pandas as pd
import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class IESOPostgresClient:
    """
    PostgreSQL client for IESO electricity data.

    Provides connection pooling, query methods, and data validation
    for the IESO demand forecasting agent.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        sslmode: str = "require",
        min_connections: int = 1,
        max_connections: int = 10
    ):
        """
        Initialize PostgreSQL client with connection pooling.

        Args:
            host: PostgreSQL host (defaults to PGHOST env var)
            database: Database name (defaults to PGDATABASE env var)
            user: Database user (defaults to PGUSER env var)
            password: Database password (defaults to PGPASSWORD env var)
            sslmode: SSL mode (default: require)
            min_connections: Minimum connections in pool
            max_connections: Maximum connections in pool
        """
        self.host = host or os.getenv("PGHOST")
        self.database = database or os.getenv("PGDATABASE")
        self.user = user or os.getenv("PGUSER")
        self.password = password or os.getenv("PGPASSWORD")
        self.sslmode = sslmode or os.getenv("PGSSLMODE", "require")

        # Validate credentials
        if not all([self.host, self.database, self.user, self.password]):
            raise ValueError(
                "Missing database credentials. Set PGHOST, PGDATABASE, "
                "PGUSER, and PGPASSWORD environment variables."
            )

        # Create connection pool
        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                min_connections,
                max_connections,
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                sslmode=self.sslmode
            )
            print(f"✓ PostgreSQL connection pool created ({min_connections}-{max_connections} connections)")
        except Exception as e:
            raise ConnectionError(f"Failed to create connection pool: {e}")

    @contextmanager
    def get_connection(self):
        """
        Context manager for getting a connection from the pool.

        Yields:
            psycopg2.connection: Database connection

        Example:
            with client.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM table")
        """
        conn = self.connection_pool.getconn()
        try:
            yield conn
        finally:
            self.connection_pool.putconn(conn)

    @contextmanager
    def get_cursor(self, cursor_factory=None):
        """
        Context manager for getting a cursor.

        Args:
            cursor_factory: Cursor factory (e.g., RealDictCursor)

        Yields:
            psycopg2.cursor: Database cursor
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()

    def test_connection(self) -> Dict[str, Any]:
        """
        Test the database connection and return connection info.

        Returns:
            dict: Connection status and metadata
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT version();")
                pg_version = cursor.fetchone()[0]

                cursor.execute("SELECT current_database();")
                db_name = cursor.fetchone()[0]

                cursor.execute("SELECT current_user;")
                db_user = cursor.fetchone()[0]

                return {
                    "success": True,
                    "host": self.host,
                    "database": db_name,
                    "user": db_user,
                    "postgresql_version": pg_version,
                    "message": "Connection successful"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Connection failed"
            }

    def get_demand_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        table: str = "00_RAW.00_IESO_DEMAND",
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Retrieve IESO demand data from PostgreSQL.

        Args:
            start_date: Start date (ISO format YYYY-MM-DD) or None for all data
            end_date: End date (ISO format YYYY-MM-DD) or None for all data
            table: Table name (default: 00_RAW.00_IESO_DEMAND)
            limit: Maximum number of rows to return

        Returns:
            pd.DataFrame: Demand data with columns [Date, Hour, Ontario_Demand, Market_Demand]

        Example:
            df = client.get_demand_data(
                start_date="2025-09-01",
                end_date="2025-09-21"
            )
        """
        # Build query
        query = f'SELECT * FROM "{table.split(".")[0]}"."{table.split(".")[1]}"'
        params = []

        # Add date filters
        where_clauses = []
        if start_date:
            where_clauses.append('"Date" >= %s')
            params.append(start_date)
        if end_date:
            where_clauses.append('"Date" <= %s')
            params.append(end_date)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += ' ORDER BY "Date", "Hour"'

        if limit:
            query += f" LIMIT {limit}"

        # Execute query
        try:
            with self.get_connection() as conn:
                df = pd.read_sql(query, conn, params=params if params else None)

            # Convert Date column to datetime if it's not already
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])

            return df
        except Exception as e:
            raise RuntimeError(f"Failed to fetch demand data: {e}")

    def get_zonal_demand_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        zones: Optional[List[str]] = None,
        normalized: bool = True
    ) -> pd.DataFrame:
        """
        Retrieve zonal demand data (demand by geographic region).

        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            zones: List of zones to filter (e.g., ['Toronto', 'Ottawa'])
            normalized: Use normalized table (01_PRI) vs wide format (00_RAW)

        Returns:
            pd.DataFrame: Zonal demand data
        """
        if normalized:
            table = '"01_PRI"."01_IESO_ZONAL_DEMAND"'
        else:
            table = '"00_RAW"."00_IESO_ZONAL_DEMAND"'

        query = f"SELECT * FROM {table}"
        params = []
        where_clauses = []

        if start_date:
            where_clauses.append('"Date" >= %s')
            params.append(start_date)
        if end_date:
            where_clauses.append('"Date" <= %s')
            params.append(end_date)
        if zones and normalized:
            placeholders = ','.join(['%s'] * len(zones))
            where_clauses.append(f'"Zone" IN ({placeholders})')
            params.extend(zones)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += ' ORDER BY "Date", "Hour"'

        try:
            with self.get_connection() as conn:
                df = pd.read_sql(query, conn, params=params if params else None)

            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])

            return df
        except Exception as e:
            raise RuntimeError(f"Failed to fetch zonal demand data: {e}")

    def get_data_freshness(self, table: str = "00_RAW.00_IESO_DEMAND") -> Dict[str, Any]:
        """
        Check when data was last updated in the specified table.

        Args:
            table: Table name to check

        Returns:
            dict: Information about data freshness
        """
        schema, table_name = table.split(".")
        query = f'''
            SELECT
                MAX("Date") as latest_date,
                COUNT(*) as total_rows,
                MIN("Date") as earliest_date
            FROM "{schema}"."{table_name}"
        '''

        try:
            with self.get_cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()

                latest_date = result[0]
                total_rows = result[1]
                earliest_date = result[2]

                # Calculate staleness
                if latest_date:
                    now = datetime.now()
                    if isinstance(latest_date, datetime):
                        hours_old = (now - latest_date).total_seconds() / 3600
                    else:
                        # If it's a date object, convert to datetime
                        latest_dt = datetime.combine(latest_date, datetime.min.time())
                        hours_old = (now - latest_dt).total_seconds() / 3600
                else:
                    hours_old = None

                return {
                    "success": True,
                    "table": table,
                    "latest_date": str(latest_date) if latest_date else None,
                    "earliest_date": str(earliest_date) if earliest_date else None,
                    "total_rows": total_rows,
                    "hours_old": round(hours_old, 1) if hours_old is not None else None,
                    "is_stale": hours_old > 48 if hours_old is not None else True,  # Stale if > 2 days old
                    "message": f"Latest data: {latest_date}, {round(hours_old, 1) if hours_old else 'N/A'} hours old"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to check data freshness"
            }

    def get_data_summary(self, table: str = "00_RAW.00_IESO_DEMAND") -> Dict[str, Any]:
        """
        Get summary statistics for the demand data.

        Args:
            table: Table name

        Returns:
            dict: Summary statistics
        """
        schema, table_name = table.split(".")
        query = f'''
            SELECT
                COUNT(*) as total_rows,
                MIN("Ontario_Demand") as min_demand,
                MAX("Ontario_Demand") as max_demand,
                AVG("Ontario_Demand") as avg_demand,
                MIN("Date") as earliest_date,
                MAX("Date") as latest_date
            FROM "{schema}"."{table_name}"
        '''

        try:
            with self.get_cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()

                return {
                    "success": True,
                    "table": table,
                    "total_rows": result[0],
                    "min_demand_mw": result[1],
                    "max_demand_mw": result[2],
                    "avg_demand_mw": round(result[3], 2) if result[3] else None,
                    "earliest_date": str(result[4]) if result[4] else None,
                    "latest_date": str(result[5]) if result[5] else None,
                    "message": f"Data summary for {table}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get data summary"
            }

    def close(self):
        """Close all connections in the pool."""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("✓ PostgreSQL connection pool closed")


# Convenience function for quick access
def get_client() -> IESOPostgresClient:
    """
    Get a configured IESO PostgreSQL client using environment variables.

    Returns:
        IESOPostgresClient: Configured client instance

    Example:
        client = get_client()
        df = client.get_demand_data(start_date="2025-09-01")
        client.close()
    """
    return IESOPostgresClient()


# Example usage
if __name__ == "__main__":
    print("=" * 80)
    print("IESO PostgreSQL Client Test")
    print("=" * 80)

    # Create client
    client = get_client()

    # Test connection
    print("\n1. Testing connection...")
    conn_info = client.test_connection()
    if conn_info["success"]:
        print(f"   ✓ Connected to {conn_info['database']} as {conn_info['user']}")
    else:
        print(f"   ✗ Connection failed: {conn_info['error']}")
        exit(1)

    # Check data freshness
    print("\n2. Checking data freshness...")
    freshness = client.get_data_freshness()
    if freshness["success"]:
        print(f"   ✓ {freshness['message']}")
        print(f"   Total rows: {freshness['total_rows']:,}")

    # Get data summary
    print("\n3. Getting data summary...")
    summary = client.get_data_summary()
    if summary["success"]:
        print(f"   ✓ Min demand: {summary['min_demand_mw']:,} MW")
        print(f"   ✓ Max demand: {summary['max_demand_mw']:,} MW")
        print(f"   ✓ Avg demand: {summary['avg_demand_mw']:,} MW")

    # Fetch sample data
    print("\n4. Fetching last 48 hours of data...")
    df = client.get_demand_data(limit=48)
    print(f"   ✓ Retrieved {len(df)} rows")
    print("\n   Sample data:")
    print(df.head().to_string(index=False))

    # Close client
    print("\n5. Closing connection...")
    client.close()

    print("\n" + "=" * 80)
    print("Test complete!")
    print("=" * 80)
