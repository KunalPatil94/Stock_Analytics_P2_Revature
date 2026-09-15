# Multi-Exchange Stock Analytics Platform

An end-to-end **Data Engineering project** using **AWS S3, Snowpipe, Snowflake, dbt, and Snowflake Native Streamlit**.

The platform ingests stock-market source data, transforms it through a layered warehouse architecture, preserves historical company information using **SCD Type 2**, exposes reusable semantic models, and serves the results through an interactive analytics dashboard.

---

## 📌 Project Overview

The platform works with four source domains:

- Companies
- Stock Exchanges
- Daily Stock Prices
- Corporate Actions

### End-to-End Flow

```text
Source CSV Files
      ↓
    AWS S3
      ↓
 External Stage
      ↓
   Snowpipe
      ↓
    RAW
      ↓
 dbt STAGING
      ↓
 Snowflake DW
      ↓
 Semantic Layer
      ↓
 Snowflake Native Streamlit
```

The main objective is to demonstrate a practical, explainable Data Engineering pipeline:

**Ingest → Transform → Model → Test → Serve → Analyze**

---

## 🏗️ Architecture

```text
                    ┌───────────────────┐
                    │   Source CSVs     │
                    └─────────┬─────────┘
                              ↓
                    ┌───────────────────┐
                    │      AWS S3       │
                    │  Object Storage   │
                    └─────────┬─────────┘
                              ↓
                    ┌───────────────────┐
                    │ Snowflake Stage   │
                    │  External Stage   │
                    └─────────┬─────────┘
                              ↓
                    ┌───────────────────┐
                    │     Snowpipe      │
                    │    Ingestion      │
                    └─────────┬─────────┘
                              ↓
             ┌────────────────────────────────┐
             │             RAW                │
             │ Companies / Exchanges / Prices│
             │ Corporate Actions             │
             └───────────────┬────────────────┘
                             ↓
                    ┌───────────────────┐
                    │    dbt STAGING    │
                    │ Clean + Standardize│
                    └─────────┬─────────┘
                              ↓
                    ┌───────────────────┐
                    │  Snowflake DW     │
                    │ Dimensions + Facts│
                    └─────────┬─────────┘
                              ↓
                    ┌───────────────────┐
                    │  Semantic Layer   │
                    │ Business-ready SQL│
                    └─────────┬─────────┘
                              ↓
                    ┌───────────────────┐
                    │ Native Streamlit  │
                    │ Analytics App     │
                    └───────────────────┘
```

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **AWS S3** | Source file storage |
| **Snowflake** | Cloud data warehouse and analytics |
| **Snowpipe** | File ingestion into RAW |
| **dbt** | Transformation, modeling, snapshots and testing |
| **SQL** | Transformation and analytical logic |
| **Altair** | Interactive dashboard visualizations |
| **Snowflake Native Streamlit** | Analytics application |
| **Git / GitHub** | Version control |

---

## 📂 Source Data

### `stock_companies.csv`

Company-level information:

- Company ID
- Ticker
- Company Name
- Sector
- Industry
- Market Cap Band
- Country
- Primary Exchange
- Status
- Listed Since
- Updated At

### `stock_exchanges.csv`

Exchange information:

- Exchange ID
- Exchange Code
- Country
- Currency
- Timezone
- Market Type
- Status
- Established Date
- Updated At

### `stock_prices_daily.csv`

Daily price information:

- Price ID
- Trade Date
- Company ID
- Exchange ID
- Open
- High
- Low
- Close
- Adjusted Close
- Volume
- VWAP
- Updated At

### `stock_corporate_actions.csv`

Corporate-action information:

- Action ID
- Company ID
- Ticker
- Action Type
- Ex Date
- Record Date
- Pay Date
- Action Value
- Ratio
- Currency
- Status
- Updated At

---

## ☁️ S3 Structure

```text
kunal-patil-stock-bucket/
│
├── companies/
│   └── stock_companies.csv
│
├── exchanges/
│   └── stock_exchanges.csv
│
├── prices/
│   └── stock_prices_daily.csv
│
└── corporate_actions/
    └── stock_corporate_actions.csv
```

Separate prefixes keep source domains organized and make ingestion configuration easier to maintain.

---

## ❄️ Snowflake RAW Layer

```text
STOCK_ANALYTICS
└── RAW
    ├── S3_STOCK_STAGE
    ├── STOCK_COMPANIES_PIPE
    ├── STOCK_EXCHANGES_PIPE
    ├── STOCK_PRICES_PIPE
    ├── STOCK_CORPORATE_ACTIONS_PIPE
    │
    ├── RAW_COMPANIES
    ├── RAW_EXCHANGES
    ├── RAW_PRICES_DAILY
    └── RAW_CORPORATE_ACTIONS
```

The RAW layer keeps ingested data close to its source structure.

This creates a clear separation between:

**Ingestion → RAW → Transformation**

---

## 🔄 dbt Transformation

```text
RAW
 ↓
STAGING
 ↓
DW
 ↓
SEM
```

### STAGING

Responsible for:

- Cleaning
- Standardization
- Type conversion
- Source relationships
- Basic data-quality checks

Staging models are implemented as **views**.

### DW

Contains the dimensional warehouse:

- Dimensions
- Facts
- Historical company versions
- Business relationships

DW models are implemented as **tables**.

### SEM

Contains business-ready analytical views used by the dashboard.

---

## ⭐ Data Warehouse Model

```text
                         DIM_COMPANY
                              │
                              │
DIM_EXCHANGE ───── FACT_DAILY_PRICE ───── DIM_DATE
                              │
                              │
                              ▼
                    FACT_CORPORATE_ACTIONS
```

### Dimensions

#### DIM_COMPANY

SCD Type 2 company dimension.

Preserves historical company attribute versions.

#### DIM_EXCHANGE

Type 1 exchange reference dimension.

#### DIM_DATE

Reusable date dimension for analytical queries.

### Facts

#### FACT_DAILY_PRICE

**Grain: one company/exchange price record for a trading date.**

Contains:

- Open
- High
- Low
- Close
- Adjusted Close
- Volume
- VWAP

#### FACT_CORPORATE_ACTIONS

Contains company corporate-action events including:

- Action type
- Event dates
- Value
- Ratio
- Currency
- Status

---

## 🕐 SCD Type 2

`DIM_COMPANY` uses a dbt snapshot-based approach to preserve historical versions.

Instead of overwriting a changed company record:

```text
Version 1
───────────────
EFF_START
        │
        │ attribute change
        ↓
Version 2
──────────────────────── Current
```

The dimension maintains:

- Surrogate Key
- Effective Start
- Effective End
- Current Flag
- Historical Versions

### Why SCD Type 2?

It allows historical records to be interpreted using the company attributes that were valid at that point in time.

---

## 🔗 Historical As-Of Join

When joining facts to an SCD Type 2 dimension, the correct dimension version must be selected based on the event date.

Conceptually:

```sql
COMPANY_ID matches
AND EVENT_DATE >= EFF_START
AND (
    EVENT_DATE < EFF_END
    OR EFF_END IS NULL
)
```

This prevents historical facts from incorrectly receiving current company attributes.

---

## 🧠 Semantic Layer

The semantic layer centralizes reusable business logic.

### STOCK_DAILY_ANALYTICS

Combines:

- Daily prices
- Company information
- Exchange information
- Date attributes
- Currency context

### COMPANY_PERFORMANCE

Provides company-level metrics such as:

- Trading days
- First/last trading date
- Period low/high
- Average close
- Average volume
- Average VWAP
- Total volume
- Turnover

### MARKET_MOVERS

Provides:

- Gainers
- Losers
- Volume leaders
- Daily returns
- Daily range

### SECTOR_EXCHANGE_SUMMARY

Provides:

- Sector metrics
- Exchange metrics
- Company counts
- Trading records
- Volume
- Turnover
- Average price/return metrics

### Design Principle

**Business logic stays in SQL. Presentation stays in Streamlit.**

---

## 📊 Streamlit Dashboard

The project includes a **Snowflake Native Streamlit** application.

### Dashboard Pages

- Platform Overview
- Market Overview
- Market Movers
- Company Detail
- Price History
- Sector & Exchange
- Corporate Actions
- Stock Screener

### Features

- Interactive filters
- Market overview
- Gainers and losers
- Volume analysis
- Company drill-down
- Price history
- Sector comparison
- Exchange analysis
- Corporate-action information
- Stock screening
- CSV export

### Visualizations

The application uses Altair for:

- Ranked bar charts
- Gain/loss charts
- Donut charts
- Candlestick charts
- Volume charts
- Activity charts
- Return distributions

---

## 🧪 Data Quality

Data quality is handled through dbt tests and business-rule validation.

### dbt Tests

- Not-null
- Unique
- Relationships
- Dimension validation
- Fact relationships
- Price-data grain

### Business Rules

```text
HIGH >= OPEN
HIGH >= CLOSE

LOW <= OPEN
LOW <= CLOSE

VOLUME >= 0
```

### Validation Flow

```text
RAW
 ↓
STAGING TESTS
 ↓
DW TESTS
 ↓
FACT GRAIN VALIDATION
 ↓
BUSINESS RULES
 ↓
SEMANTIC LAYER
```

---

## 📁 Project Structure

```text
stock_analytics/
│
├── models/
│   ├── staging/
│   │   ├── sources.yml
│   │   ├── staging.yml
│   │   ├── stg_companies.sql
│   │   ├── stg_exchanges.sql
│   │   ├── stg_prices_daily.sql
│   │   └── stg_corporate_actions.sql
│   │
│   ├── dw/
│   │   ├── dim_company.sql
│   │   ├── dim_exchange.sql
│   │   ├── dim_date.sql
│   │   ├── fact_daily_price.sql
│   │   ├── fact_corporate_actions.sql
│   │   └── dw.yml
│   │
│   └── sem/
│       ├── stock_daily_analytics.sql
│       ├── company_performance.sql
│       ├── market_movers.sql
│       ├── sector_exchange_summary.sql
│       └── sem.yml
│
├── snapshots/
│   └── dim_company_snapshot.sql
│
├── seeds/
│   ├── fx_rates_usd.csv
│   └── seeds.yml
│
├── macros/
│   ├── cents_to_dollars.sql
│   └── generate_schema_name.sql
│
├── tests/
│   └── stg_price_daily_grain.sql
│
├── dbt_project.yml
├── packages.yml
├── streamlit_app.py
└── README.md
```

---

## 🚀 Setup

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd stock_analytics
```

### 2. Configure Snowflake

Create/configure:

```text
Database:
STOCK_ANALYTICS

Schemas:
RAW
STAGING
DW
SEM
```

Configure the required:

- S3 external stage
- File formats
- RAW tables
- Snowpipes
- Snowflake permissions

> Never commit AWS or Snowflake credentials to GitHub.

### 3. Configure dbt

Configure the `stock_analytics` profile locally.

Example:

```yaml
stock_analytics:
  target: dev

  outputs:
    dev:
      type: snowflake
      account: <account>
      user: <user>
      password: <password>
      role: <role>
      database: STOCK_ANALYTICS
      warehouse: <warehouse>
      schema: STAGING
      threads: 4
```

Keep credentials outside the repository.

### 4. Install dbt Dependencies

```bash
dbt deps
```

### 5. Load Source Data

Upload the four CSV files into the configured S3 prefixes:

```text
companies/
exchanges/
prices/
corporate_actions/
```

Snowpipe loads the files into the corresponding RAW tables.

### 6. Run dbt

```bash
dbt parse
```

```bash
dbt build
```

Or run components separately:

```bash
dbt seed
dbt run
dbt test
```

### 7. Run Streamlit

Open the Streamlit application in Snowflake and run/deploy `streamlit_app.py`.

The application uses:

```python
from snowflake.snowpark.context import get_active_session
```

so it queries Snowflake directly through the active Snowpark session.

---

## 🔍 Verification

### RAW

```sql
SELECT COUNT(*) FROM STOCK_ANALYTICS.RAW.RAW_COMPANIES;
SELECT COUNT(*) FROM STOCK_ANALYTICS.RAW.RAW_EXCHANGES;
SELECT COUNT(*) FROM STOCK_ANALYTICS.RAW.RAW_PRICES_DAILY;
SELECT COUNT(*) FROM STOCK_ANALYTICS.RAW.RAW_CORPORATE_ACTIONS;
```

### DW

```sql
SELECT COUNT(*) FROM STOCK_ANALYTICS.DW.DIM_COMPANY;
SELECT COUNT(*) FROM STOCK_ANALYTICS.DW.DIM_EXCHANGE;
SELECT COUNT(*) FROM STOCK_ANALYTICS.DW.DIM_DATE;
SELECT COUNT(*) FROM STOCK_ANALYTICS.DW.FACT_DAILY_PRICE;
SELECT COUNT(*) FROM STOCK_ANALYTICS.DW.FACT_CORPORATE_ACTIONS;
```

### SEM

```sql
SELECT * FROM STOCK_ANALYTICS.SEM.STOCK_DAILY_ANALYTICS LIMIT 10;

SELECT * FROM STOCK_ANALYTICS.SEM.MARKET_MOVERS LIMIT 10;

SELECT * FROM STOCK_ANALYTICS.SEM.COMPANY_PERFORMANCE LIMIT 10;

SELECT * FROM STOCK_ANALYTICS.SEM.SECTOR_EXCHANGE_SUMMARY LIMIT 10;
```

---

## 🎯 Key Engineering Decisions

| Decision | Reason |
|---|---|
| **S3 + Snowpipe** | Separate source storage from ingestion |
| **dbt** | Modular transformations and testing |
| **SCD Type 2** | Preserve company history |
| **As-of joins** | Maintain historical correctness |
| **Star schema** | Analytics-friendly warehouse design |
| **Semantic layer** | Centralize business logic |
| **Native Streamlit** | Snowflake-native data consumption |

The guiding principle is:

**Every layer has a clear responsibility.**

---

## ⚠️ Scope & Engineering Judgment

The project intentionally avoids adding complexity that the available source data cannot justify.

### No fabricated market calendar

The source data does not provide an authoritative exchange trading calendar.

### No invented corporate actions

Corporate-action records are based on the provided source data.

### No misleading 20-day volatility

The seed dataset is relatively small and sparse, so advanced rolling volatility metrics are not treated as core project metrics.

### No duplicated business logic

The Streamlit application consumes curated semantic models rather than recreating warehouse logic.

### No unnecessary orchestration

The project focuses on demonstrating the core Data Engineering architecture clearly instead of adding unnecessary tooling.

---

## 💡 What This Project Demonstrates

- AWS S3
- Snowflake
- Snowpipe
- External stages
- RAW data ingestion
- dbt transformations
- dbt snapshots
- SCD Type 2
- Surrogate keys
- Effective dating
- Historical as-of joins
- Fact and dimension modeling
- Star schema
- Semantic layer
- dbt testing
- Data-quality validation
- SQL analytics
- Snowpark
- Snowflake Native Streamlit
- Interactive visualization
- Git/GitHub

---

## 📈 Future Enhancements

- S3 event-driven Snowpipe auto-ingestion
- Pipeline monitoring and load auditing
- Larger historical market dataset
- Authoritative exchange calendars
- Snowflake Cortex Analyst
- Cortex Search / RAG
- CI/CD
- RBAC and governance
- Automated deployment

---

## 🧑‍💻 Interview Explanation

> I built an end-to-end stock analytics Data Engineering platform using AWS S3, Snowpipe, Snowflake, dbt and Snowflake Native Streamlit. Source CSV files are stored in S3 and ingested into Snowflake RAW tables through Snowpipe. dbt performs staging, transformation, testing and dimensional modeling. I implemented DIM_COMPANY as an SCD Type 2 dimension and used historical as-of joins so facts receive the correct company version. The warehouse contains dimensions and fact tables, while a semantic layer exposes reusable business logic for the dashboard. Finally, Snowflake Native Streamlit provides interactive market, company, sector, exchange and screening analytics.

---

## 🏆 Project Highlights

```text
✓ AWS S3 source ingestion
✓ Snowpipe-based loading
✓ Snowflake Data Warehouse
✓ dbt transformation layer
✓ dbt snapshots
✓ SCD Type 2
✓ Historical as-of joins
✓ Star-schema modeling
✓ Fact and dimension tables
✓ Semantic layer
✓ Data-quality testing
✓ Snowflake Native Streamlit
✓ Interactive analytics
✓ Git/GitHub version control
```

---

## 📜 License

This project is intended for educational, portfolio and demonstration purposes.

---

## 👤 Author

**Kunal R. Patil**

Computer Engineering  
Data Engineering | Snowflake | dbt | SQL | Cloud Data Platforms

GitHub: `https://github.com/KunalPatil94`

LinkedIn: `https://www.linkedin.com/in/kunal-r-patil-a2975325a/`
