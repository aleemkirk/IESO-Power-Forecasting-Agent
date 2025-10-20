# IESO Power Consumption Forecasting Agent

An autonomous AI agent that fetches real-time electricity consumption data from Ontario's Independent Electricity System Operator (IESO) and generates forecasts using local AI models.

## Key Features

- **100% Local Execution** - All processing runs on your MacBook
- **Local LLM** - Uses Llama 3.1 8B via Ollama (no API costs)
- **Agentic Architecture** - LangGraph-based agent with autonomous decision-making
- **Real-time Data** - Pulls data from PostgreSQL database with IESO data
- **Time Series Forecasting** - Prophet and ARIMA models for predictions
- **Tool-based Design** - Agent uses tools to fetch data, train models, and generate forecasts

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.10+** installed
2. **Ollama** installed: `brew install ollama`
3. **Llama 3.1 8B model**: `ollama pull llama3.1`
4. **PostgreSQL database** with IESO data (Neon DB configured)
5. **8GB+ RAM** (16GB recommended)

## Installation

1. Clone the repository:
```bash
cd /Users/aleemkhan/PycharmProjects/IESO-Power-Forecasting-Agent
```

2. Activate the conda environment:
```bash
conda activate IESO-Power-Forecasting-Agent
```

3. Install dependencies (already done):
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
   - The `.env` file is already created with your PostgreSQL credentials
   - DO NOT commit `.env` to git (it's in .gitignore)

## Quick Start

1. Start Ollama service (in a separate terminal):
```bash
ollama serve
```

2. Run the agent:
```bash
python main.py
```

## Project Structure

```
ieso-forecast-agent/
├── config/              # Configuration files
├── src/                 # Source code
│   ├── agents/         # Agent orchestrator and tools
│   ├── data/           # PostgreSQL client and caching
│   ├── models/         # Forecasting models (Prophet, ARIMA)
│   ├── utils/          # Utilities and validators
│   └── visualization/  # Plotting functions
├── data/               # Data storage
├── models/             # Trained model artifacts
├── outputs/            # Forecasts and reports
├── tests/              # Unit and integration tests
└── main.py            # Entry point
```

## Development Status

### Phase 1: Foundation ✅ (COMPLETED)
- [x] Install Ollama and Llama 3.1 8B
- [x] Create project structure
- [x] Set up Python environment and requirements.txt
- [ ] Create basic agent loop with LangGraph
- [ ] Test Llama 3.1 with simple tool calling

### Phase 2: PostgreSQL Data Integration (Next)
- [ ] Explore existing PostgreSQL schema and tables
- [ ] Document data structure, columns, and date ranges
- [ ] Build `pg_client.py` - PostgreSQL connection wrapper
- [ ] Implement `query_ieso_data` tool for fetching data
- [ ] Test data retrieval and validation

## Technology Stack

- **LangGraph 0.2.x** - Agent orchestration
- **Ollama + Llama 3.1 8B** - Local LLM
- **PostgreSQL (Neon)** - Data storage
- **Prophet & ARIMA** - Time series forecasting
- **pandas, numpy** - Data processing
- **matplotlib, plotly** - Visualization

## Useful Commands

```bash
# Start Ollama
ollama serve

# Run agent
python main.py

# Run tests
pytest tests/

# Format code
black src/

# Lint code
ruff check src/
```

## Documentation

See [CLAUDE.md](CLAUDE.md) for detailed documentation including:
- Agent architecture and design principles
- Tool definitions and patterns
- PostgreSQL connection details
- Implementation phases
- Testing strategy

## License

MIT

## Contributing

This is a personal project. For issues or questions, please contact the repository owner.
