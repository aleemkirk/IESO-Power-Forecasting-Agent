"""
IESO Power Forecasting Agent - Main Entry Point

This is the main entry point for the IESO Power Forecasting Agent.
The agent autonomously fetches electricity consumption data from Ontario's
IESO and generates forecasts using local AI models.
"""

import os
import sys
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

    print("\n" + "=" * 60)
    print("IESO Power Forecasting Agent - Phase 1")
    print("=" * 60)
    print(f"Ollama Host: {os.getenv('OLLAMA_HOST')}")
    print(f"Ollama Model: {os.getenv('OLLAMA_MODEL')}")
    print(f"Database: {os.getenv('PGDATABASE')} @ {os.getenv('PGHOST')}")
    print("=" * 60)

    # Check for test mode
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("\n=== Running Quick Test ===\n")
        run_test()
        return

    # Initialize and run agent
    try:
        from src.agents.orchestrator import IESOForecastAgent

        agent = IESOForecastAgent(
            model_name=os.getenv("OLLAMA_MODEL", "llama3.1"),
            temperature=0.1
        )

        logger.info("Agent initialized successfully")
        print("\nAgent initialized successfully!")
        print("Starting interactive mode...\n")

        # Run in interactive mode
        agent.run_interactive()

    except Exception as e:
        logger.error(f"Error initializing agent: {e}")
        print(f"\nError: {e}")
        print("\nMake sure Ollama is running: ollama serve")
        sys.exit(1)


def run_test():
    """Run a quick test of the agent."""
    try:
        from src.agents.orchestrator import IESOForecastAgent

        agent = IESOForecastAgent(
            model_name=os.getenv("OLLAMA_MODEL", "llama3.1"),
            temperature=0.1
        )

        print("Agent initialized successfully!")
        print("\nTest 1: Checking system status...")
        response = agent.run("What is the system status?")
        print(f"Response: {response}\n")

        print("Test 2: Testing tool calling...")
        response = agent.run("What time is it?")
        print(f"Response: {response}\n")

        print("Test 3: Testing calculation...")
        response = agent.run("Add 42 and 58")
        print(f"Response: {response}\n")

        print("=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)

    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"\nTest failed: {e}")
        print("\nMake sure Ollama is running: ollama serve")
        sys.exit(1)


if __name__ == "__main__":
    main()
