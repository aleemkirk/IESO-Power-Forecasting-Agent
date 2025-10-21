# IESO Database Schema Documentation

**Last Updated:** 2025-10-21
**Database:** Neon PostgreSQL (`neondb`)
**Schemas Explored:** 00_RAW, 01_PRI, 00_REF

---

## Overview

The IESO (Independent Electricity System Operator) database contains electricity demand and generation data for Ontario, Canada. The data is organized into multiple schemas with raw data in `00_RAW` and processed/normalized data in `01_PRI`.

---

## Schemas

| Schema | Purpose | Tables |
|--------|---------|--------|
| `00_RAW` | Raw IESO data as fetched from source | 4 tables |
| `01_PRI` | Processed/primary data (normalized) | 1 table |
| `00_REF` | Reference and metadata tables | 1 table |
| `02_FEA` | Feature engineering (future use) | - |
| `03_OUT` | Model outputs and forecasts (future use) | - |

---

## Primary Tables for Forecasting

### 1. `00_RAW.00_IESO_DEMAND` ⭐ MAIN TABLE FOR FORECASTING

**Purpose:** Hourly electricity demand for Ontario (Market Demand and Ontario Demand)

**Schema:**
```sql
CREATE TABLE "00_RAW"."00_IESO_DEMAND" (
    "Date" TIMESTAMP,           -- Hour beginning timestamp
    "Hour" BIGINT,               -- Hour of day (1-24)
    "Market_Demand" BIGINT,      -- Total market demand in MW
    "Ontario_Demand" BIGINT,     -- Ontario-only demand in MW
    "Modified_DT" DATE           -- Last modification date
);
```

**Data Statistics:**
- **Total Rows:** 6,290
- **Date Range:** 2025-01-01 to 2025-09-22 (265 days of hourly data)
- **Market_Demand:** 13,055 - 26,714 MW (avg: 19,035 MW)
- **Ontario_Demand:** 11,536 - 24,862 MW (avg: 16,660 MW)
- **Granularity:** Hourly (24 readings per day)
- **Completeness:** No nulls in demand columns

**Sample Data:**
```
Date                | Hour | Market_Demand | Ontario_Demand | Modified_DT
--------------------|------|---------------|----------------|-------------
2025-01-01 00:00:00 |    1 |        17,247 |         13,887 | 2025-09-20
2025-01-01 00:00:00 |    2 |        17,355 |         13,722 | 2025-09-20
2025-01-01 00:00:00 |    3 |        17,638 |         13,688 | 2025-09-20
```

**Use Cases:**
- ✅ **Primary table for demand forecasting**
- ✅ Time series modeling (Prophet, ARIMA)
- ✅ Historical trend analysis
- ✅ Peak demand prediction

**Notes:**
- `Market_Demand` includes imports/exports
- `Ontario_Demand` is internal consumption only
- Use `Ontario_Demand` for most forecasting scenarios

---

### 2. `00_RAW.00_IESO_ZONAL_DEMAND`

**Purpose:** Hourly electricity demand broken down by 10 geographic zones in Ontario

**Schema:**
```sql
CREATE TABLE "00_RAW"."00_IESO_ZONAL_DEMAND" (
    "Date" TIMESTAMP,
    "Hour" BIGINT,
    "Ontario_Demand" BIGINT,    -- Total Ontario demand
    "Northwest" BIGINT,          -- Zone: Northwest Ontario
    "Northeast" BIGINT,          -- Zone: Northeast Ontario
    "Ottawa" BIGINT,             -- Zone: Ottawa region
    "East" BIGINT,               -- Zone: Eastern Ontario
    "Toronto" BIGINT,            -- Zone: Greater Toronto Area (largest)
    "Essa" BIGINT,               -- Zone: Essa region
    "Bruce" BIGINT,              -- Zone: Bruce Peninsula
    "Southwest" BIGINT,          -- Zone: Southwest Ontario
    "Niagara" BIGINT,            -- Zone: Niagara region
    "West" BIGINT,               -- Zone: Western Ontario
    "Zone_Total" BIGINT,         -- Sum of all zones
    "Diff" BIGINT,               -- Difference (Ontario_Demand - Zone_Total)
    "Modified_DT" TIMESTAMP
);
```

**Data Statistics:**
- **Total Rows:** 6,335
- **Date Range:** 2025-01-01 to 2025-09-21
- **Ontario_Demand:** 4,598 - 26,567 MW (avg: 16,648 MW)

**Zone Statistics (Average MW):**
| Zone | Min MW | Avg MW | Max MW | % of Total |
|------|--------|--------|--------|------------|
| Toronto | 3,848 | 6,039 | 10,100 | 36% (largest) |
| Southwest | 2,125 | 3,251 | 5,031 | 19% |
| West | 1,169 | 1,860 | 2,758 | 11% |
| Northeast | 919 | 1,312 | 1,725 | 8% |
| Essa | 566 | 1,069 | 1,877 | 6% |
| Ottawa | 639 | 1,035 | 1,780 | 6% |
| East | 304 | 967 | 1,635 | 6% |
| Niagara | 356 | 582 | 903 | 3% |
| Northwest | 298 | 519 | 761 | 3% |
| Bruce | 64 | 115 | 218 | 1% |

**Use Cases:**
- ✅ Regional demand forecasting
- ✅ Identify geographic patterns
- ✅ Peak load analysis by zone
- ✅ Multi-output forecasting models

---

### 3. `01_PRI.01_IESO_ZONAL_DEMAND` (Normalized Version)

**Purpose:** Same as above but in long/normalized format (one row per zone per hour)

**Schema:**
```sql
CREATE TABLE "01_PRI"."01_IESO_ZONAL_DEMAND" (
    "Date" TIMESTAMP,
    "Hour" BIGINT,
    "Modified_DT" TIMESTAMP,
    "Ontario_Demand" BIGINT,
    "Zone_Total" BIGINT,
    "Diff" BIGINT,
    "Zone" TEXT,                 -- Zone name (e.g., "Toronto", "Ottawa")
    "Value" BIGINT               -- Demand for this specific zone
);
```

**Data Statistics:**
- **Total Rows:** 63,350 (6,335 hours × 10 zones)
- **Date Range:** 2025-01-01 to 2025-09-21
- **Value Range:** 64 - 10,100 MW (avg: 1,675 MW per zone)

**Use Cases:**
- ✅ Better for machine learning models
- ✅ Easier to filter by specific zones
- ✅ Time series analysis per zone
- ✅ Recommended for agent tools

**Notes:**
- Preferred over wide format `00_RAW.00_IESO_ZONAL_DEMAND` for most ML tasks
- Each hour appears 10 times (once per zone)

---

### 4. `00_RAW.00_GEN_OUTPUT_BY_FUEL_TYPE_HOURLY`

**Purpose:** Hourly electricity generation by fuel type

**Schema:**
```sql
CREATE TABLE "00_RAW"."00_GEN_OUTPUT_BY_FUEL_TYPE_HOURLY" (
    "Date" TIMESTAMP,
    "hour" BIGINT,
    "fuel_type" TEXT,            -- NUCLEAR, GAS, HYDRO, WIND, SOLAR, etc.
    "output" DOUBLE PRECISION    -- Generation output in MW
);
```

**Data Statistics:**
- **Total Rows:** 42,168
- **Date Range:** 2025-01-01 to 2025-09-21
- **Output Range:** 0 - 10,441 MW (avg: 2,811 MW per fuel type)

**Fuel Type Breakdown:**
| Fuel Type | Description | Typical Output |
|-----------|-------------|----------------|
| NUCLEAR | Base load nuclear plants (Bruce, Pickering, Darlington) | ~10,000+ MW |
| HYDRO | Hydroelectric generation | ~3,000-4,000 MW |
| WIND | Wind farms | Variable (0-3,000 MW) |
| GAS | Natural gas plants | Variable (200-2,000 MW) |
| SOLAR | Solar panels | Daytime only (0-1,000 MW) |

**Use Cases:**
- ✅ Understanding supply mix
- ✅ Renewable energy analysis
- ✅ Supply-demand matching
- ✅ Forecasting generation needs

**Notes:**
- Solar output is 0 during night hours
- Nuclear provides base load (~10,400 MW constant)
- Wind and gas are variable/dispatchable

---

### 5. `00_RAW.00_GEN_OUTPUT_CAPABILITY_HOURLY`

**Purpose:** Generator-level output, capability, and availability

**Schema:**
```sql
CREATE TABLE "00_RAW"."00_GEN_OUTPUT_CAPABILITY_HOURLY" (
    "Date" DATE,
    "Hour" BIGINT,
    "GeneratorName" TEXT,        -- Specific generator ID (e.g., "BRUCEA-G1")
    "FuelType" TEXT,
    "OutputEnergy" DOUBLE PRECISION,      -- Actual output in MW
    "CapabilityEnergy" DOUBLE PRECISION,  -- Maximum possible output
    "AvailCapacity" DOUBLE PRECISION      -- Available capacity
);
```

**Data Statistics:**
- **Total Rows:** 11,244
- **Date Range:** 2025-09-20 to 2025-09-22 (recent data only)
- **OutputEnergy:** 0 - 1,309 MW (avg: 90 MW per generator)
- **CapabilityEnergy:** 0 - 1,590 MW (avg: 139 MW)

**Use Cases:**
- ✅ Generator performance analysis
- ✅ Capacity planning
- ✅ Outage detection
- ⚠️ Limited historical data (only 3 days)

---

### 6. `00_REF.00_TABLE_REGISTER`

**Purpose:** Metadata and tracking for all tables in the database

**Schema:**
```sql
CREATE TABLE "00_REF"."00_TABLE_REGISTER" (
    "ID" INTEGER PRIMARY KEY,
    "TABLE_NAME" TEXT,
    "TABLE_SCHEMA" TEXT,
    "MODIFIED_DT" DATE,
    "DESCRIPTION" TEXT,
    "ROW_COUNT" BIGINT,
    "SOURCE_URL" TEXT,
    "MODIFIED_TIME" TIME,
    "CREATED_DT" DATE,
    "CREATED_TIME" TIME
);
```

**Data Statistics:**
- **Total Rows:** 604 tracking entries
- Tracks all data loads and updates

**Use Cases:**
- ✅ Check when tables were last updated
- ✅ Monitor data pipeline health
- ✅ Audit data loads

---

## Recommended Tables for Agent Tools

### For Demand Forecasting (Primary Use Case):
1. **`00_RAW.00_IESO_DEMAND`** - Ontario-wide demand (simplest, recommended for v1)
2. **`01_PRI.01_IESO_ZONAL_DEMAND`** - Regional demand (for advanced forecasting)

### For Analysis:
3. **`00_RAW.00_GEN_OUTPUT_BY_FUEL_TYPE_HOURLY`** - Generation mix analysis
4. **`00_REF.00_TABLE_REGISTER`** - Data freshness checks

---

## Data Quality Notes

### ✅ Strengths:
- **Complete hourly coverage** from Jan 1, 2025 to Sept 21-22, 2025
- **No missing values** in critical demand columns
- **Consistent granularity** (hourly data)
- **Well-structured schemas** with clear separation of raw/processed data

### ⚠️ Considerations:
- **Limited history:** Only ~9 months of data (Jan-Sept 2025)
- **Seasonal coverage:** Missing Oct-Dec data (will need to account for seasonal patterns)
- **Generator data:** Only 3 days of detailed generator-level data
- **Future data:** No 2024 or earlier years available

### 🔧 Recommendations for Forecasting:
1. **Use `00_RAW.00_IESO_DEMAND` as primary source**
2. **Ontario_Demand column** is best for forecasting (excludes imports/exports)
3. **Extract temporal features:** Day of week, hour of day, month, holidays
4. **Consider weather data:** Temperature strongly correlates with demand (not in DB currently)
5. **Train/test split:** Use first 7-8 months for training, last month for testing
6. **Seasonal adjustments:** May need to extrapolate winter patterns from limited data

---

## SQL Query Examples

### Get Latest 7 Days for Training
```sql
SELECT "Date", "Hour", "Ontario_Demand"
FROM "00_RAW"."00_IESO_DEMAND"
WHERE "Date" >= NOW() - INTERVAL '7 days'
ORDER BY "Date", "Hour";
```

### Get Data Freshness
```sql
SELECT MAX("Date") as latest_data
FROM "00_RAW"."00_IESO_DEMAND";
```

### Get Peak Demand by Month
```sql
SELECT
    DATE_TRUNC('month', "Date") as month,
    MAX("Ontario_Demand") as peak_demand,
    AVG("Ontario_Demand") as avg_demand
FROM "00_RAW"."00_IESO_DEMAND"
GROUP BY DATE_TRUNC('month', "Date")
ORDER BY month;
```

### Get Zonal Demand (Normalized Format)
```sql
SELECT "Date", "Hour", "Zone", "Value"
FROM "01_PRI"."01_IESO_ZONAL_DEMAND"
WHERE "Zone" = 'Toronto'
  AND "Date" >= '2025-09-01'
ORDER BY "Date", "Hour";
```

---

## Connection Details

**Environment Variables (from `.env`):**
```bash
PGHOST=ep-noisy-frost-aelel7na-pooler.c-2.us-east-2.aws.neon.tech
PGDATABASE=neondb
PGUSER=neondb_owner
PGPASSWORD=***  # See .env file
PGSSLMODE=require
PGCHANNELBINDING=require
```

**Important:** Schema and table names starting with numbers must be quoted in SQL:
```sql
-- ❌ Wrong
SELECT * FROM 00_RAW.00_IESO_DEMAND;

-- ✅ Correct
SELECT * FROM "00_RAW"."00_IESO_DEMAND";
```

---

## Next Steps for Agent Development

1. ✅ **Database exploration complete**
2. ⏭️ **Build `pg_client.py`** - PostgreSQL connection wrapper
3. ⏭️ **Create agent tools:**
   - `query_ieso_demand(start_date, end_date)` → returns demand data
   - `check_data_freshness()` → checks latest available data
   - `validate_data_quality(df)` → checks for gaps/anomalies
4. ⏭️ **Implement forecasting models** (Prophet, ARIMA)
5. ⏭️ **Test end-to-end forecast generation**

---

**Generated by:** `explore_db.py`
**For more details, see:** `db_exploration_results.txt`
