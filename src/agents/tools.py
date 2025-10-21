"""
Agent Tools for IESO Power Forecasting Agent

This module contains all the tools that the agent can use to:
- Fetch IESO electricity demand data
- Check data quality and freshness
- Analyze demand patterns
- Generate forecasts (future)

Phase 2: Real IESO data tools
"""

from langchain_core.tools import tool
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import random
import pandas as pd
import sys
import os

# Add parent directory to path to import pg_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.pg_client import get_client


# ============================================================================
# DATA TOOLS - Fetch and query IESO electricity data
# ============================================================================

@tool
def check_data_freshness() -> Dict[str, Any]:
    """Check when IESO demand data was last updated in the database.

    Use this tool to verify data is recent before making forecasts.

    Returns:
        Dictionary with data freshness information including:
        - latest_date: Most recent data timestamp
        - hours_old: How many hours since last update
        - is_stale: Boolean indicating if data is >48 hours old
        - total_rows: Total records in database

    Example:
        Agent should call this before fetching data to ensure freshness.
    """
    try:
        client = get_client()
        result = client.get_data_freshness()
        client.close()
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to check data freshness"
        }


@tool
def get_data_summary() -> Dict[str, Any]:
    """Get statistical summary of IESO electricity demand data.

    Provides overview of demand patterns including min, max, and average demand.

    Returns:
        Dictionary with summary statistics:
        - min_demand_mw: Minimum demand in megawatts
        - max_demand_mw: Maximum demand in megawatts
        - avg_demand_mw: Average demand in megawatts
        - earliest_date: First available data point
        - latest_date: Most recent data point
        - total_rows: Number of records

    Example:
        Use to understand demand range before forecasting.
    """
    try:
        client = get_client()
        result = client.get_data_summary()
        client.close()
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get data summary"
        }


@tool
def query_ieso_demand_data(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    days_back: int = 7
) -> Dict[str, Any]:
    """Query IESO electricity demand data from PostgreSQL database.

    Fetches hourly Ontario electricity demand data for the specified date range.
    If no dates provided, returns last 7 days of data.

    Args:
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
        days_back: If no dates specified, how many days to look back (default: 7)

    Returns:
        Dictionary with:
        - success: Boolean indicating if query succeeded
        - data: List of demand records (each with Date, Hour, Ontario_Demand, Market_Demand)
        - record_count: Number of records returned
        - date_range: [earliest, latest] dates in result
        - avg_demand: Average demand in MW
        - peak_demand: Maximum demand in MW

    Example:
        To get last 7 days: query_ieso_demand_data()
        To get specific range: query_ieso_demand_data(start_date="2025-09-01", end_date="2025-09-15")
    """
    try:
        client = get_client()

        # If no dates provided, use days_back
        if not start_date and not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        # Fetch data
        df = client.get_demand_data(start_date=start_date, end_date=end_date)
        client.close()

        if df.empty:
            return {
                "success": False,
                "message": "No data found for specified date range",
                "record_count": 0
            }

        # Convert DataFrame to list of dicts for LLM consumption
        data_records = df.to_dict('records')

        # Calculate summary statistics
        avg_demand = df['Ontario_Demand'].mean()
        peak_demand = df['Ontario_Demand'].max()
        min_demand = df['Ontario_Demand'].min()

        return {
            "success": True,
            "data": data_records[:100],  # Limit to 100 records to avoid context overflow
            "record_count": len(df),
            "date_range": [
                str(df['Date'].min()),
                str(df['Date'].max())
            ],
            "avg_demand_mw": round(avg_demand, 2),
            "peak_demand_mw": int(peak_demand),
            "min_demand_mw": int(min_demand),
            "message": f"Retrieved {len(df)} hourly demand records from {start_date} to {end_date}"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to query demand data: {str(e)}"
        }


@tool
def validate_data_quality(start_date: str, end_date: str) -> Dict[str, Any]:
    """Validate quality of IESO data for a given date range.

    Checks for missing hours, gaps, outliers, and data completeness.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Dictionary with validation results:
        - is_valid: Boolean overall quality assessment
        - missing_hours: Number of missing hourly records
        - has_gaps: Boolean indicating if there are gaps
        - outliers: Number of outlier values
        - completeness_pct: Percentage of expected hours present
        - issues: List of quality issues found

    Example:
        Before training a model, validate data quality.
    """
    try:
        client = get_client()
        df = client.get_demand_data(start_date=start_date, end_date=end_date)
        client.close()

        if df.empty:
            return {
                "is_valid": False,
                "message": "No data found for validation"
            }

        # Calculate expected hours
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        expected_hours = int((end_dt - start_dt).total_seconds() / 3600) + 24  # +24 for inclusive

        actual_hours = len(df)
        missing_hours = expected_hours - actual_hours
        completeness = (actual_hours / expected_hours) * 100

        # Check for outliers (demand > 3 std dev from mean)
        mean_demand = df['Ontario_Demand'].mean()
        std_demand = df['Ontario_Demand'].std()
        outliers = df[
            (df['Ontario_Demand'] > mean_demand + 3 * std_demand) |
            (df['Ontario_Demand'] < mean_demand - 3 * std_demand)
        ]

        # Check for gaps in time series
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')
        time_diffs = df['Date'].diff()
        expected_diff = pd.Timedelta(hours=1)
        gaps = time_diffs[time_diffs > expected_diff * 1.5]  # Allow 1.5x tolerance

        issues = []
        if missing_hours > 0:
            issues.append(f"{missing_hours} missing hours out of {expected_hours} expected")
        if len(outliers) > 0:
            issues.append(f"{len(outliers)} outlier values detected")
        if len(gaps) > 0:
            issues.append(f"{len(gaps)} time gaps detected")

        is_valid = completeness >= 95 and len(outliers) < actual_hours * 0.01  # <1% outliers

        return {
            "success": True,
            "is_valid": is_valid,
            "expected_hours": expected_hours,
            "actual_hours": actual_hours,
            "missing_hours": missing_hours,
            "completeness_pct": round(completeness, 2),
            "outlier_count": len(outliers),
            "gap_count": len(gaps),
            "has_gaps": len(gaps) > 0,
            "issues": issues if issues else ["No quality issues detected"],
            "message": "Data validation complete"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to validate data: {str(e)}"
        }


@tool
def calculate_demand_statistics(start_date: str, end_date: str) -> Dict[str, Any]:
    """Calculate statistical metrics for electricity demand over a date range.

    Computes mean, median, std dev, percentiles, and identifies peak demand times.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Dictionary with statistics:
        - mean_demand: Average demand in MW
        - median_demand: Median demand in MW
        - std_dev: Standard deviation
        - percentiles: 25th, 50th, 75th, 95th percentiles
        - peak_hour: Hour of day with highest average demand
        - min_hour: Hour of day with lowest average demand
    """
    try:
        client = get_client()
        df = client.get_demand_data(start_date=start_date, end_date=end_date)
        client.close()

        if df.empty:
            return {
                "success": False,
                "message": "No data available for statistics"
            }

        demand = df['Ontario_Demand']

        # Basic statistics
        stats = {
            "success": True,
            "mean_demand_mw": round(demand.mean(), 2),
            "median_demand_mw": round(demand.median(), 2),
            "std_dev_mw": round(demand.std(), 2),
            "min_demand_mw": int(demand.min()),
            "max_demand_mw": int(demand.max()),
            "percentiles": {
                "p25": int(demand.quantile(0.25)),
                "p50": int(demand.quantile(0.50)),
                "p75": int(demand.quantile(0.75)),
                "p95": int(demand.quantile(0.95))
            }
        }

        # Peak hour analysis
        hourly_avg = df.groupby('Hour')['Ontario_Demand'].mean()
        stats["peak_hour"] = int(hourly_avg.idxmax())
        stats["peak_hour_avg_mw"] = round(hourly_avg.max(), 2)
        stats["min_hour"] = int(hourly_avg.idxmin())
        stats["min_hour_avg_mw"] = round(hourly_avg.min(), 2)

        stats["message"] = f"Statistics calculated for {len(df)} hours of data"

        return stats

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to calculate statistics: {str(e)}"
        }


# ============================================================================
# UTILITY TOOLS
# ============================================================================

@tool
def get_current_time() -> str:
    """Get the current date and time.

    Returns:
        String with current date and time in ISO format.
    """
    return datetime.now().isoformat()


# ============================================================================
# TOOL REGISTRY
# ============================================================================

# All tools available to the agent
ALL_TOOLS = [
    # Data Tools
    check_data_freshness,
    get_data_summary,
    query_ieso_demand_data,
    validate_data_quality,
    calculate_demand_statistics,

    # Utility Tools
    get_current_time
]
