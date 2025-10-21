"""
Quick script to explore the PostgreSQL database schema.
This will help us understand what IESO data is available.
"""

import os
import psycopg2
from dotenv import load_dotenv
from tabulate import tabulate

# Load environment variables
load_dotenv()

def explore_database():
    """Connect to database and explore the schema."""

    print("=" * 80)
    print("IESO DATABASE EXPLORATION")
    print("=" * 80)

    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=os.getenv("PGHOST"),
            database=os.getenv("PGDATABASE"),
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
            sslmode=os.getenv("PGSSLMODE"),
        )

        print("\n✓ Successfully connected to PostgreSQL!")
        print(f"  Host: {os.getenv('PGHOST')}")
        print(f"  Database: {os.getenv('PGDATABASE')}\n")

        cursor = conn.cursor()

        # 1. List all schemas
        print("-" * 80)
        print("1. AVAILABLE SCHEMAS")
        print("-" * 80)

        cursor.execute("""
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            ORDER BY schema_name;
        """)

        schemas = cursor.fetchall()
        if schemas:
            for i, (schema_name,) in enumerate(schemas, 1):
                print(f"{i}. {schema_name}")
        else:
            print("No user schemas found.")

        print()

        # 2. List all tables in all schemas (focusing on IESO data schemas)
        print("-" * 80)
        print("2. AVAILABLE TABLES (focusing on 00_RAW and 01_PRI schemas)")
        print("-" * 80)

        cursor.execute("""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema IN ('00_RAW', '01_PRI', 'public')
               OR table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            ORDER BY table_schema, table_name;
        """)

        tables = cursor.fetchall()
        if tables:
            for i, (schema_name, table_name) in enumerate(tables, 1):
                print(f"{i}. {schema_name}.{table_name}")
        else:
            print("No tables found.")

        print()

        # 3. For each table, show structure and sample data
        for (schema_name, table_name) in tables:
            full_table_name = f'"{schema_name}"."{table_name}"'
            display_name = f"{schema_name}.{table_name}"
            print("-" * 80)
            print(f"3. TABLE: {display_name}")
            print("-" * 80)

            # Get column information
            cursor.execute(f"""
                SELECT
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = '{schema_name}' AND table_name = '{table_name}'
                ORDER BY ordinal_position;
            """)

            columns = cursor.fetchall()

            print("\nColumn Structure:")
            headers = ["Column Name", "Data Type", "Nullable", "Default"]
            print(tabulate(columns, headers=headers, tablefmt="grid"))

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {full_table_name};")
            row_count = cursor.fetchone()[0]
            print(f"\nTotal Rows: {row_count:,}")

            # Get date range if timestamp column exists
            timestamp_cols = [col[0] for col in columns if 'timestamp' in col[0].lower() or 'date' in col[0].lower()]

            if timestamp_cols:
                ts_col = timestamp_cols[0]
                cursor.execute(f"""
                    SELECT
                        MIN("{ts_col}") as earliest,
                        MAX("{ts_col}") as latest
                    FROM {full_table_name};
                """)
                date_range = cursor.fetchone()
                print(f"\nDate Range ({ts_col}):")
                print(f"  Earliest: {date_range[0]}")
                print(f"  Latest:   {date_range[1]}")

            # Show sample data (first 5 rows)
            cursor.execute(f"SELECT * FROM {full_table_name} LIMIT 5;")
            sample_data = cursor.fetchall()

            if sample_data:
                print("\nSample Data (first 5 rows):")
                col_names = [desc[0] for desc in cursor.description]
                print(tabulate(sample_data, headers=col_names, tablefmt="grid"))

            # Show some basic statistics for numeric columns
            numeric_cols = [col[0] for col in columns if col[1] in ('integer', 'numeric', 'double precision', 'real', 'bigint')]

            if numeric_cols:
                print("\nNumeric Column Statistics:")
                for col in numeric_cols:
                    cursor.execute(f"""
                        SELECT
                            '{col}' as column_name,
                            MIN("{col}") as min_val,
                            AVG("{col}") as avg_val,
                            MAX("{col}") as max_val,
                            COUNT(CASE WHEN "{col}" IS NULL THEN 1 END) as null_count
                        FROM {full_table_name};
                    """)
                    stats = cursor.fetchone()
                    print(f"\n  {col}:")
                    print(f"    Min: {stats[1]}")
                    print(f"    Avg: {stats[2]}")
                    print(f"    Max: {stats[3]}")
                    print(f"    Nulls: {stats[4]}")

            print()

        # Close connection
        cursor.close()
        conn.close()

        print("=" * 80)
        print("EXPLORATION COMPLETE")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ Error connecting to database: {e}")
        print("\nTroubleshooting:")
        print("1. Verify .env file has correct credentials")
        print("2. Check if PostgreSQL server is accessible")
        print("3. Ensure SSL mode is configured correctly")

if __name__ == "__main__":
    explore_database()
