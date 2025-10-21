"""
Agent Tools for IESO Power Forecasting Agent

This module contains all the tools that the agent can use.
For Phase 1, we start with simple test tools.
"""

from langchain_core.tools import tool
from typing import Dict, Any
from datetime import datetime
import random


@tool
def get_current_time() -> str:
    """Get the current date and time.

    Returns:
        String with current date and time in ISO format.
    """
    return datetime.now().isoformat()


@tool
def add_numbers(a: float, b: float) -> Dict[str, Any]:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Dictionary with the sum and the operation performed.
    """
    result = a + b
    return {
        "operation": f"{a} + {b}",
        "result": result,
        "timestamp": datetime.now().isoformat()
    }


@tool
def check_system_status() -> Dict[str, Any]:
    """Check the agent system status.

    Returns:
        Dictionary with system status information.
    """
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "ollama_model": "llama3.1",
        "agent_version": "0.1.0-phase1"
    }


@tool
def simulate_data_fetch(num_records: int = 10) -> Dict[str, Any]:
    """Simulate fetching data (placeholder for real IESO data fetch).

    Args:
        num_records: Number of records to simulate

    Returns:
        Dictionary with simulated data and metadata.
    """
    simulated_data = [
        {
            "timestamp": datetime.now().isoformat(),
            "demand_mw": round(random.uniform(15000, 25000), 2),
            "temperature_c": round(random.uniform(-10, 30), 1)
        }
        for _ in range(num_records)
    ]

    return {
        "success": True,
        "data": simulated_data,
        "message": f"Simulated {num_records} records",
        "metadata": {
            "record_count": num_records,
            "data_type": "simulated",
            "timestamp": datetime.now().isoformat()
        }
    }


# Tool list for easy import
ALL_TOOLS = [
    get_current_time,
    add_numbers,
    check_system_status,
    simulate_data_fetch
]
