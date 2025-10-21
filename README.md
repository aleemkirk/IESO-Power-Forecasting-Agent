# IESO Power Forecasting Agent

An autonomous AI agent that forecasts Ontario electricity consumption using local LLMs and time series models.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.x-green.svg)](https://langchain-ai.github.io/langgraph/)
[![Ollama](https://img.shields.io/badge/Ollama-Llama%203.1-orange.svg)](https://ollama.ai/)

## Overview

This project implements an **agentic AI system** that autonomously:
- Fetches real-time electricity consumption data from Ontario's IESO (Independent Electricity System Operator)
- Analyzes historical patterns using advanced time series models
- Generates accurate power consumption forecasts
- Makes intelligent decisions about data freshness, model selection, and forecast parameters

**Key Features:**
- 100% local execution - no API costs, no cloud dependencies
- Powered by Llama 3.1 8B via Ollama
- LangGraph-based agentic architecture with autonomous decision-making
- Prophet and ARIMA forecasting models
- PostgreSQL integration for historical data storage
- Interactive CLI interface

---

## Architecture

### Agentic Decision Loop

The agent follows a **PERCEIVE → REASON → PLAN → ACT → REFLECT → ADAPT** cycle:

```
┌─────────────────────────────────────────────────────────┐
│                     USER REQUEST                        │
│          "What will peak demand be tomorrow?"           │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │   PERCEIVE     │  Check data freshness, model status
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │    REASON      │  Llama 3.1 analyzes situation
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │     PLAN       │  Generate tool execution plan
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │      ACT       │  Execute tools (query DB, train model)
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │    REFLECT     │  Validate results
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │     ADAPT      │  Loop back if needed
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │    RESPOND     │  Return forecast to user
         └────────────────┘
```

### Agent Tools

The agent has access to specialized tools for autonomous operation:

**Data Tools:**
- `check_data_freshness()` - Verify when data was last updated
- `query_ieso_data()` - Retrieve electricity consumption data from PostgreSQL
- `validate_data_quality()` - Check for missing values and anomalies
- `get_data_summary()` - Generate statistical summaries

**Model Tools:**
- `train_model()` - Train Prophet or ARIMA forecasting models
- `evaluate_model_performance()` - Calculate accuracy metrics (MAPE, RMSE)
- `generate_forecast()` - Create predictions for specified time horizons
- `compare_models()` - Determine best performing model

**Analysis Tools:**
- `calculate_statistics()` - Compute statistical metrics
- `detect_anomalies()` - Identify outliers in demand patterns
- `create_visualization()` - Generate forecast plots

**Meta Tools:**
- `log_decision()` - Record agent reasoning and actions
- `get_performance_history()` - Retrieve past forecast accuracy

---

## Technology Stack

### Core Framework
- **LangGraph 0.2.x** - State machine orchestration
- **LangChain 0.3.x** - Agent tools and abstractions
- **Ollama** - Local LLM runtime
- **Llama 3.1 8B** - Language model for reasoning

### Data & Forecasting
- **pandas** - Data manipulation
- **numpy** - Numerical operations
- **Prophet** - Facebook's time series forecasting library
- **statsmodels** - ARIMA/SARIMA models
- **scikit-learn** - ML utilities

### Database & Storage
- **PostgreSQL (Neon)** - Historical IESO data storage
- **SQLAlchemy** - Database ORM
- **psycopg2-binary** - PostgreSQL adapter

### Visualization
- **matplotlib** - Static plots
- **plotly** - Interactive visualizations

---

## Installation

### Prerequisites

**System Requirements:**
- macOS, Linux, or Windows with WSL
- Python 3.10 or higher
- 8GB+ RAM (16GB recommended)
- ~10GB free disk space

### Step 1: Install Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from [https://ollama.ai/download](https://ollama.ai/download)

### Step 2: Pull Llama 3.1 Model

```bash
# Download the Llama 3.1 8B model (~4.7GB)
ollama pull llama3.1

# Verify installation
ollama run llama3.1
```

Type `/bye` to exit the Ollama interactive session.

### Step 3: Start Ollama Service

```bash
# Start Ollama server in background
ollama serve
```

Keep this running in a separate terminal or run as a background service.

### Step 4: Clone and Setup Project

```bash
# Clone the repository
git clone https://github.com/yourusername/ieso-forecast-agent.git
cd ieso-forecast-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# PostgreSQL Connection (Neon Database)
PGHOST=ep-noisy-frost-aelel7na-pooler.c-2.us-east-2.aws.neon.tech
PGDATABASE=neondb
PGUSER=neondb_owner
PGPASSWORD=your_password_here
PGSSLMODE=require
PGCHANNELBINDING=require

# Or use connection string format:
# DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1

# Model Settings
DEFAULT_FORECAST_HORIZON=24
DEFAULT_CONFIDENCE_LEVEL=0.95

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/agent.log
```

**IMPORTANT:** Never commit `.env` to version control! Ensure `.gitignore` includes `.env`.

---

## Data Sources

### IESO (Independent Electricity System Operator)

The project uses electricity consumption data from Ontario's **IESO**, which operates the province's power grid.

**Data Coverage:**
- **Geographic Scope:** Ontario, Canada
- **Granularity:** 5-minute intervals (typical)
- **Metrics:** Demand (MW), Price, Generation by fuel type
- **Historical Range:** Multiple years of data

### PostgreSQL Database Schema

Your IESO data is stored in a **Neon PostgreSQL** database.

**Connection Details:**
- Host: `ep-noisy-frost-aelel7na-pooler.c-2.us-east-2.aws.neon.tech`
- Database: `neondb`
- SSL: Required

**Expected Tables:** (Verify against your actual schema)
```sql
-- Demand table (primary data source)
CREATE TABLE demand (
    timestamp TIMESTAMPTZ NOT NULL,
    demand_mw NUMERIC(10, 2),
    zone VARCHAR(50),
    PRIMARY KEY (timestamp, zone)
);

-- Price table (optional)
CREATE TABLE price (
    timestamp TIMESTAMPTZ NOT NULL,
    price_cad NUMERIC(10, 2),
    zone VARCHAR(50)
);
```

**Common Queries:**
```sql
-- Get latest data
SELECT MAX(timestamp) FROM demand;

-- Retrieve last 7 days for forecasting
SELECT * FROM demand
WHERE timestamp >= NOW() - INTERVAL '7 days'
ORDER BY timestamp;

-- Check data completeness
SELECT DATE(timestamp), COUNT(*) as records
FROM demand
GROUP BY DATE(timestamp)
ORDER BY DATE(timestamp) DESC
LIMIT 30;
```

---

## Usage

### Quick Start

```bash
# Ensure Ollama is running
ollama serve

# Run the agent
python main.py
```

### Interactive Mode

```
IESO Power Forecasting Agent - Phase 1
============================================================
Ollama Host: http://localhost:11434
Ollama Model: llama3.1
Database: neondb @ ep-noisy-frost-aelel7na-pooler...
============================================================

Agent initialized successfully!
Starting interactive mode...

> What will peak demand be tomorrow?

[Agent analyzes request, fetches data, trains model, generates forecast]

Based on latest data from PostgreSQL, I forecast peak demand
tomorrow at 5:00 PM EST will be 23,450 MW (±500 MW, 95% confidence).

Historical pattern analysis shows typical weekday evening peaks
around this time. Current weather forecasts suggest mild temperatures,
which should keep demand moderate.

>
```

### Test Mode

```bash
# Run quick tests
python main.py test
```

### Example Use Cases

**1. Next-Day Forecast:**
```
> Generate a 24-hour forecast starting from tomorrow morning
```

**2. Data Quality Check:**
```
> Check if we have fresh data and validate quality
```

**3. Model Comparison:**
```
> Compare Prophet vs ARIMA for next week's forecast
```

**4. Anomaly Detection:**
```
> Are there any unusual patterns in last week's demand data?
```

---

## Project Structure

```
ieso-forecast-agent/
├── .env                          # Environment variables (DO NOT COMMIT)
├── .gitignore
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── CLAUDE.md                     # Development guide
│
├── config/
│   ├── agent_config.yaml        # Agent behavior settings
│   └── model_config.yaml        # Model hyperparameters
│
├── src/
│   ├── __init__.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── orchestrator.py      # Main LangGraph agent
│   │   ├── tools.py             # Agent tool definitions
│   │   └── prompts.py           # Llama-optimized prompts
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── pg_client.py         # PostgreSQL connection
│   │   └── cache.py             # Local caching
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── prophet_model.py     # Prophet forecaster
│   │   ├── arima_model.py       # ARIMA forecaster
│   │   └── base_model.py        # Base forecaster interface
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py            # Logging configuration
│   │   └── validators.py        # Data validation
│   │
│   └── visualization/
│       ├── __init__.py
│       └── plots.py             # Plotting functions
│
├── data/
│   ├── raw/                     # Raw IESO data
│   ├── processed/               # Cleaned data
│   └── cache/                   # Local cache files
│
├── models/
│   └── saved_models/            # Trained model artifacts
│
├── outputs/
│   ├── forecasts/               # Generated predictions (CSV, JSON)
│   └── reports/                 # Visualizations (PNG, HTML)
│
├── tests/
│   ├── __init__.py
│   ├── test_tools.py            # Tool unit tests
│   ├── test_agent.py            # Agent integration tests
│   └── test_ieso_client.py      # Database connection tests
│
├── logs/
│   └── agent.log                # Application logs
│
└── main.py                      # Entry point
```

---

## Development Roadmap

### Phase 1: Foundation ✅ COMPLETED
- [x] Install Ollama and Llama 3.1 8B
- [x] Create project structure
- [x] Set up Python environment and dependencies
- [x] Create basic agent loop with LangGraph
- [x] Test Llama 3.1 tool calling

### Phase 2: PostgreSQL Data Integration 🚧 IN PROGRESS
- [ ] Explore existing PostgreSQL schema and tables
- [ ] Document data structure and date ranges
- [ ] Build `pg_client.py` - PostgreSQL wrapper
- [ ] Implement `query_ieso_data` tool
- [ ] Test data retrieval and validation
- [ ] Implement local caching (optional)

### Phase 3: Forecasting Models
- [ ] Implement Prophet model wrapper
- [ ] Implement ARIMA model wrapper
- [ ] Create `train_model` tool
- [ ] Create `generate_forecast` tool
- [ ] Test models on historical data

### Phase 4: Agent Intelligence
- [ ] Build all remaining agent tools
- [ ] Optimize prompts for Llama 3.1
- [ ] Implement decision-making logic
- [ ] Add reflection and validation
- [ ] Test various forecast scenarios

### Phase 5: Memory & Learning
- [ ] Implement performance tracking
- [ ] Build agent learning loop
- [ ] Add decision logging
- [ ] Create improvement metrics

### Phase 6: Interface & Deployment
- [ ] Build CLI interface
- [ ] Add scheduling for auto-forecasts
- [ ] Create visualization dashboard
- [ ] Write comprehensive documentation

---

## Testing

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test Suite
```bash
# Test database connection
pytest tests/test_ieso_client.py -v

# Test agent tools
pytest tests/test_tools.py -v

# Test agent decision-making
pytest tests/test_agent.py -v
```

### Test Coverage
```bash
pytest --cov=src tests/
```

---

## Performance Benchmarks

### Target Performance Metrics

**Functional:**
- **Forecast Accuracy:** <10% MAPE for 24-hour forecasts
- **Data Retrieval:** <2 seconds for 7-day historical queries
- **Model Training:** <30 seconds for Prophet/ARIMA
- **End-to-End Forecast:** <60 seconds from request to result

**Agentic Behavior:**
- Agent autonomously decides when to refresh data
- Agent selects optimal forecasting model based on data characteristics
- Agent validates outputs and requests human intervention for anomalies
- Agent learns from forecast errors and adapts strategies

**System Performance:**
- Llama 3.1 response time: <10 seconds
- Memory usage: <2GB during operation
- No memory leaks over 7+ day continuous runs

---

## Troubleshooting

### Ollama Connection Issues

**Problem:** `Connection refused to localhost:11434`

**Solution:**
```bash
# Start Ollama service
ollama serve

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

### Database Connection Errors

**Problem:** `SSL connection error` or `authentication failed`

**Solution:**
1. Verify `.env` credentials are correct
2. Check SSL mode is set to `require`
3. Test connection manually:
```python
import psycopg2
conn = psycopg2.connect(
    host="your-host",
    database="neondb",
    user="neondb_owner",
    password="your-password",
    sslmode="require"
)
print(conn.get_dsn_parameters())
```

### Model Installation Issues

**Problem:** `prophet` installation fails on macOS

**Solution:**
```bash
# Install C++ compiler dependencies
brew install cmake

# Install prophet with conda (alternative)
conda install -c conda-forge prophet
```

### Memory Issues with Llama 3.1

**Problem:** Ollama crashes or runs slowly

**Solution:**
1. Close other memory-intensive applications
2. Use smaller context windows in prompts
3. Consider using `llama3.1:latest` (quantized version)

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Code Style:**
- Use `black` for formatting: `black src/`
- Use `ruff` for linting: `ruff check src/`
- Add type hints where possible
- Write docstrings for all functions

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **IESO** - Ontario's Independent Electricity System Operator for providing open data
- **Ollama Team** - For making local LLMs accessible
- **Meta AI** - For Llama 3.1
- **LangChain** - For the agentic framework
- **Facebook Research** - For the Prophet forecasting library

---

## Resources

- **LangGraph Documentation:** [https://langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/)
- **Ollama Documentation:** [https://ollama.ai/](https://ollama.ai/)
- **IESO Data Portal:** [https://www.ieso.ca/en/Power-Data](https://www.ieso.ca/en/Power-Data)
- **Prophet Docs:** [https://facebook.github.io/prophet/](https://facebook.github.io/prophet/)
- **PostgreSQL Python:** [https://www.psycopg.org/](https://www.psycopg.org/)
- **Neon PostgreSQL:** [https://neon.tech/docs](https://neon.tech/docs)

---

## Contact

For questions or support, please open an issue on GitHub or contact the maintainer.

**Project Link:** [https://github.com/yourusername/ieso-forecast-agent](https://github.com/yourusername/ieso-forecast-agent)

---

## Useful Commands

```bash
# Start Ollama service
ollama serve

# Activate virtual environment
source venv/bin/activate

# Run the agent
python main.py

# Run tests
pytest tests/

# Format code
black src/

# Lint code
ruff check src/

# Check dependencies
pip list

# Update dependencies
pip install --upgrade -r requirements.txt
```

---

**Built with 100% local execution - No cloud, no API costs, full privacy.**
