"""
IESO Power Forecasting Agent - Main Entry Point

This is the main entry point for the IESO Power Forecasting Agent.
The agent autonomously fetches electricity consumption data from Ontario's
IESO and generates forecasts using local AI models.
"""

import os
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
log_file = os.getenv("LOG_FILE", "logs/agent.log")

logger.add(
    log_file,
    rotation="500 MB",
    retention="10 days",
    level=log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)


def main():
    """Main entry point for the IESO Power Forecasting Agent."""
    logger.info("Starting IESO Power Forecasting Agent...")

    # TODO: Initialize agent
    # TODO: Start agent loop

    print("IESO Power Forecasting Agent")
    print("=" * 50)
    print("Environment: Initialized")
    print(f"Ollama Host: {os.getenv('OLLAMA_HOST')}")
    print(f"Ollama Model: {os.getenv('OLLAMA_MODEL')}")
    print(f"Database: {os.getenv('PGDATABASE')} @ {os.getenv('PGHOST')}")
    print("=" * 50)
    print("\nAgent is ready but not yet implemented.")
    print("Next steps: Implement agent orchestrator and tools.")


if __name__ == "__main__":
    main()
