# IESO Power Consumption Forecasting Agent

## Project Overview

Build an autonomous AI agent that fetches real-time electricity consumption data from Ontario's Independent Electricity System Operator (IESO) and generates forecasts for power consumption using local AI models.

## Key Requirements

- **100% Local Execution**: All processing runs on local MacBook
- **Local LLM**: Uses Llama 3.1 8B via Ollama (no API costs)
- **Agentic Architecture**: LangGraph-based agent with autonomous decision-making
- **Real-time Data**: Pulls live data from IESO public APIs
- **Time Series Forecasting**: Prophet and ARIMA models for predictions
- **Tool-based Design**: Agent uses tools to fetch data, train models, and generate forecasts

## Technology Stack

### Core Agentic Framework
- **LangGraph 0.2.x** - State machine and workflow orchestration
- **Ollama** - Local LLM runtime for Llama 3.1 8B
- **LangChain 0.3.x** - Agent tools and abstractions
- **langchain-ollama** - Ollama integration

### Data & Forecasting
- **pandas 2.2.x** - Data manipulation
- **numpy 1.26.x** - Numerical operations
- **prophet 1.1.x** - Facebook's forecasting library
- **statsmodels 0.14.x** - ARIMA/SARIMA models
- **scikit-learn 1.5.x** - ML utilities

### Storage & Visualization
- **sqlalchemy 2.0.x** - Database ORM
- **psycopg2-binary 2.9.x** - PostgreSQL adapter
- **sqlite3** (built-in) - Local cache (optional)
- **matplotlib 3.9.x** - Plotting
- **plotly 5.24.x** - Interactive visualizations

### Utilities
- **python-dotenv 1.0.x** - Environment variables
- **loguru 0.7.x** - Enhanced logging
- **schedule 1.2.x** - Task scheduling

## Prerequisites

### System Requirements
- macOS (user has MacBook)
- Python 3.10+
- 8GB+ RAM (16GB recommended)
- ~10GB free disk space

### Before Starting
User should have installed:
1. **Ollama**: `brew install ollama`
2. **Llama 3.1 8B model**: `ollama pull llama3.1`
3. **Verified Ollama works**: `ollama run llama3.1`

## Project Structure

```
ieso-forecast-agent/
├── .env                          # Configuration (create this)
├── .gitignore
├── requirements.txt
├── README.md
├── CLAUDE.md                     # This file
├── config/
│   ├── agent_config.yaml        # Agent behavior settings
│   └── model_config.yaml        # Model hyperparameters
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── orchestrator.py      # Main LangGraph agent coordinator
│   │   ├── tools.py             # All agent tools (data, model, analysis)
│   │   └── prompts.py           # Llama-optimized prompts
│   ├── data/
│   │   ├── __init__.py
│   │   ├── pg_client.py         # PostgreSQL connection and queries
│   │   └── cache.py             # Local caching (optional)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── prophet_model.py     # Prophet forecaster
│   │   ├── arima_model.py       # ARIMA forecaster
│   │   └── base_model.py        # Base forecaster interface
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py            # Logging setup
│   │   └── validators.py        # Data validation
│   └── visualization/
│       ├── __init__.py
│       └── plots.py             # Plotting functions
├── data/
│   ├── raw/                     # Raw IESO data
│   ├── processed/               # Cleaned data
│   └── database.db              # SQLite database
├── models/
│   └── saved_models/            # Trained model artifacts
├── outputs/
│   ├── forecasts/               # Generated predictions
│   └── reports/                 # Visualization outputs
├── tests/
│   ├── __init__.py
│   ├── test_tools.py
│   ├── test_agent.py
│   └── test_ieso_client.py
└── main.py                      # Entry point
```

## Architecture

### Agent Loop (LangGraph State Machine)

The agent follows this cycle:

1. **PERCEIVE** - Check data freshness, model performance, system state
2. **REASON** - Llama 3.1 analyzes situation and decides what to do
3. **PLAN** - Generate list of tools to use
4. **ACT** - Execute tool calls
5. **REFLECT** - Validate results and check if goal achieved
6. **ADAPT** - Update strategy if needed, loop back if more work needed

### Agent Tools

The agent has these tools available:

**Data Tools:**
- `check_data_freshness()` - When was data last updated in PostgreSQL?
- `query_ieso_data(start, end, filters)` - Pull data from PostgreSQL
- `validate_data_quality()` - Check for missing values, outliers
- `get_data_summary()` - Statistics about available data
- `cache_data_locally(data)` - Store in local cache (optional)

**Model Tools:**
- `train_model(model_type, params)` - Train Prophet or ARIMA
- `evaluate_model_performance(model_id)` - Check accuracy metrics
- `generate_forecast(model, horizon)` - Create predictions
- `compare_models()` - Which model is best?

**Analysis Tools:**
- `calculate_statistics(data)` - Mean, std, percentiles
- `detect_anomalies(data)` - Find outliers
- `create_visualization(data, plot_type)` - Generate plots

**Meta Tools:**
- `log_decision(reasoning, action)` - Record agent decisions
- `get_performance_history()` - Past forecast accuracy

### Example Agent Flow

```
User: "What will peak demand be tomorrow?"

Agent loop:
1. PERCEIVE: check_data_freshness() → "Last record: 2 hours ago"
2. REASON: "Data is recent enough, can proceed with forecast"
3. PLAN: [query_ieso_data, validate, generate_forecast]
4. ACT: 
   - query_ieso_data(start="7 days ago", end="now")
   - validate_data_quality() → "OK, 168 hours of data"
   - generate_forecast(model="prophet", horizon="24h")
5. REFLECT: "Forecast: 23,450 MW at 5pm, seems reasonable"
6. RESPOND: "Based on latest data from PostgreSQL..."
```

## IESO Data Sources

### Existing PostgreSQL Database

**You already have IESO data in a Neon PostgreSQL database.**

**Connection Details:**
- Host: `ep-noisy-frost-aelel7na-pooler.c-2.us-east-2.aws.neon.tech`
- Database: `neondb`
- User: `neondb_owner`
- SSL Mode: `require`
- Channel Binding: `require`

**Important:** Store credentials in `.env` file, never commit to git.

### Data Schema

**TODO:** Document the PostgreSQL schema:
- What tables exist?
- What columns are available?
- What is the date range of data?
- How frequently is data updated?
- What is the data granularity (5-min, hourly, daily)?

### Typical IESO Data Structure

Expected tables/columns (verify against your actual schema):
- **demand** - Electricity consumption data
  - `timestamp` or `datetime`
  - `demand_mw` - Demand in megawatts
  - `zone` (optional) - Geographic zone
- **price** (optional) - Market pricing data
- **generation** (optional) - Generation by fuel type

### Query Examples

Common queries your agent will need:
```sql
-- Get latest data timestamp
SELECT MAX(timestamp) FROM demand;

-- Get last 24 hours of data
SELECT * FROM demand 
WHERE timestamp >= NOW() - INTERVAL '24 hours'
ORDER BY timestamp;

-- Get historical data for training
SELECT * FROM demand
WHERE timestamp >= '2024-01-01'
ORDER BY timestamp;

-- Check data completeness
SELECT DATE(timestamp), COUNT(*) as records
FROM demand
GROUP BY DATE(timestamp)
ORDER BY DATE(timestamp) DESC
LIMIT 30;
```

## Implementation Phases

### Phase 1: Foundation (Start Here)
- [x] Install Ollama and Llama 3.1 8B
- [ ] Create project structure
- [ ] Set up Python environment and requirements.txt
- [ ] Create basic agent loop with LangGraph
- [ ] Test Llama 3.1 with simple tool calling

### Phase 2: PostgreSQL Data Integration
- [ ] Explore existing PostgreSQL schema and tables
- [ ] Document data structure, columns, and date ranges
- [ ] Build `pg_client.py` - PostgreSQL connection wrapper
- [ ] Implement `query_ieso_data` tool for fetching data
- [ ] Test data retrieval and validation
- [ ] Implement local caching strategy (optional)

### Phase 3: Forecasting Models
- [ ] Implement Prophet model wrapper
- [ ] Implement ARIMA model wrapper
- [ ] Create `train_model` tool
- [ ] Create `generate_forecast` tool
- [ ] Test models on historical data

### Phase 4: Agent Intelligence
- [ ] Build all remaining agent tools
- [ ] Optimize prompts for Llama 3.1
- [ ] Implement agent decision-making logic
- [ ] Add reflection and validation
- [ ] Test agent on various scenarios

### Phase 5: Memory & Learning
- [ ] Implement performance tracking database
- [ ] Build agent learning loop
- [ ] Add decision logging
- [ ] Create agent improvement metrics

### Phase 6: Interface & Deployment
- [ ] Build CLI interface
- [ ] Add scheduling for automatic forecasts
- [ ] Create visualization dashboard (optional)
- [ ] Write documentation

## Key Design Principles

### 1. Agentic Decision-Making
The agent should **reason** about what to do, not just execute predefined steps:
- ✅ "Data is 6 hours old, should I fetch new data?" (agent decides)
- ❌ "Always fetch data at 9am" (hard-coded schedule)

### 2. Tool-First Design
Every action should be a tool that the agent can invoke:
```python
@tool
def fetch_ieso_data(start_date: str, end_date: str) -> Dict:
    """Fetches electricity demand data from IESO.
    
    Args:
        start_date: ISO format date (YYYY-MM-DD)
        end_date: ISO format date (YYYY-MM-DD)
    
    Returns:
        Dict with 'success', 'data', and 'message' keys
    """
```

### 3. Llama 3.1 Optimization
Llama needs clear, structured prompts:
- Use ReAct format (Thought → Action → Observation)
- Be explicit about tool usage
- Provide examples in system prompt
- Keep context windows reasonable (~4k tokens)

### 4. Graceful Degradation
Handle failures intelligently:
- IESO API down? → Use cached data with warning
- Model training failed? → Fall back to simpler model
- Incomplete data? → Interpolate with transparency

### 5. Transparency
Always explain reasoning:
- Log why decisions were made
- Report confidence levels
- Warn about data quality issues

## Common Patterns

### Tool Definition Pattern
```python
from langchain.tools import tool
from typing import Dict, Any
import pandas as pd

@tool
def query_ieso_data(start_date: str, end_date: str, table: str = "demand") -> Dict[str, Any]:
    """Queries IESO electricity data from PostgreSQL database.
    
    The agent will see this docstring and use it to decide
    when to invoke this tool.
    
    Args:
        start_date: ISO format date (YYYY-MM-DD)
        end_date: ISO format date (YYYY-MM-DD)
        table: Table name (default: "demand")
        
    Returns:
        Dictionary with standardized structure:
        {
            "success": bool,
            "data": pd.DataFrame or None,
            "message": str,
            "metadata": Dict (record_count, date_range, etc.)
        }
    """
    try:
        # Connect to PostgreSQL
        from src.data.pg_client import get_connection
        
        conn = get_connection()
        query = f"""
            SELECT * FROM {table}
            WHERE timestamp >= %s AND timestamp <= %s
            ORDER BY timestamp
        """
        df = pd.read_sql(query, conn, params=(start_date, end_date))
        
        return {
            "success": True,
            "data": df,
            "message": f"Retrieved {len(df)} records",
            "metadata": {
                "record_count": len(df),
                "date_range": [df['timestamp'].min(), df['timestamp'].max()],
                "columns": list(df.columns)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "message": f"Error: {str(e)}",
            "metadata": {"error_type": type(e).__name__}
        }
```

### LangGraph Agent Pattern
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, List

class AgentState(TypedDict):
    goal: str
    messages: List[Dict]
    tools_used: List[str]
    result: Optional[str]
    
def perceive(state: AgentState) -> AgentState:
    # Gather information
    return state

def reason(state: AgentState) -> AgentState:
    # Llama decides what to do
    return state

def act(state: AgentState) -> AgentState:
    # Execute tools
    return state

workflow = StateGraph(AgentState)
workflow.add_node("perceive", perceive)
workflow.add_node("reason", reason)
workflow.add_node("act", act)
# ... add edges and compile
```

## Testing Strategy

### Unit Tests
- Test each tool independently
- Mock IESO API responses
- Validate data processing functions

### Integration Tests
- Test agent loop end-to-end
- Test with real PostgreSQL data
- Test error recovery (DB connection fails, etc.)

### Agent Quality Tests
- Does agent make reasonable decisions?
- Does agent use appropriate tools?
- Does agent recover from errors?

## Success Criteria

### Functional
- [ ] Successfully query PostgreSQL for IESO data
- [ ] Generate accurate forecasts (<10% MAPE for 24h)
- [ ] Agent runs autonomously for 1+ week
- [ ] Handles errors gracefully (DB connection issues, etc.)

### Agentic Behavior
- [ ] Agent decides when to fetch data (not scheduled)
- [ ] Agent selects appropriate forecasting model
- [ ] Agent validates its own outputs
- [ ] Agent learns from mistakes

### Performance
- [ ] Llama 3.1 responds in <10 seconds
- [ ] Forecasts generate in <30 seconds
- [ ] No memory leaks over extended runs

## Important Notes

### Llama 3.1 Limitations
- Not as smart as Claude - may need more explicit prompting
- Tool calling less reliable - validate outputs carefully
- Context window ~8k tokens - manage conversation length
- May need multiple attempts for complex reasoning

### IESO Data Considerations
- Data already collected in PostgreSQL by another process
- Connection requires SSL and channel binding
- Query efficiently to minimize data transfer
- Consider local caching for frequently accessed data
- Handle PostgreSQL connection errors gracefully

### Development Tips
- Start simple, add complexity gradually
- Test agent reasoning on paper before coding
- Use verbose logging to debug agent decisions
- Keep tool functions focused and single-purpose
- Ollama runs in background - start with `ollama serve`

## Environment Variables

Create `.env` file (NEVER commit to git):
```bash
# PostgreSQL Connection (from your existing Neon DB)
PGHOST=ep-noisy-frost-aelel7na-pooler.c-2.us-east-2.aws.neon.tech
PGDATABASE=neondb
PGUSER=neondb_owner
PGPASSWORD=**********
PGSSLMODE=require
PGCHANNELBINDING=require

# Or use connection string format:
DATABASE_URL=postgresql://neondb_owner:npg_SxD9A1NmQLJF@ep-noisy-frost-aelel7na-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require

# Local Cache (optional)
LOCAL_CACHE_PATH=data/cache/
CACHE_ENABLED=true

# Model Settings
DEFAULT_FORECAST_HORIZON=24
DEFAULT_CONFIDENCE_LEVEL=0.95

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/agent.log

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1
```

**IMPORTANT:** Add `.env` to `.gitignore` immediately!

## Useful Commands

```bash
# Start Ollama service
ollama serve

# Activate virtual environment
source venv/bin/activate

# Run agent
python main.py

# Run tests
pytest tests/

# Format code
black src/

# Lint code
ruff check src/

# Interactive Python with agent loaded
python -i main.py
```

## Resources

- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **Ollama Docs**: https://ollama.ai/
- **PostgreSQL Python**: https://www.psycopg.org/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Prophet Docs**: https://facebook.github.io/prophet/
- **Statsmodels**: https://www.statsmodels.org/
- **Neon PostgreSQL**: https://neon.tech/docs

## Getting Help

When using Claude Code:
1. Reference this file for project context
2. Ask about specific implementation details
3. Request code reviews for agent decision logic
4. Get help debugging Llama prompts
5. Discuss architecture decisions

---

**Current Status**: Ready to begin Phase 1 - Foundation

**Next Steps**: 
1. Create project structure
2. Set up requirements.txt (include psycopg2-binary)
3. Test PostgreSQL connection with credentials
4. Explore database schema and document tables
5. Build basic LangGraph agent loop
6. Test Llama 3.1 tool calling