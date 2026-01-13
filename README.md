# CoinGecko E2E Data Pipeline (Airflow + Postgres)

End-to-end data pipeline that extracts cryptocurrency market data from the CoinGecko API and loads snapshot records into Postgres. Orchestrated with Apache Airflow (Docker Compose).

## What this pipeline does

- **Extract**: Calls the CoinGecko endpoint `/api/v3/coins/markets` (top N assets by market cap)
- **Load**: Inserts a **snapshot** into Postgres (`raw_coingecko_market_snapshot`)
- **Orchestrate**: Airflow DAG scheduled daily and runnable on demand

### Output table (raw layer)

`raw_coingecko_market_snapshot`

Each run writes a new snapshot keyed by:
- `snapshot_ts`
- `asset_id`

This makes it easy to build historical analytics later (e.g., price changes over time, volatility, top movers, etc.).

---

## Architecture

CoinGecko API → Airflow DAG (PythonOperator) → Postgres

---

## Tech stack

- Python
- Apache Airflow (Docker)
- Postgres (Docker)
- Docker Compose

---

## Project structure

```
e2e-data-pipeline-coingecko/
├─ airflow/
│  ├─ dags/
│  │  └─ coingecko_e2e_daily.py
│  └─ docker-compose.yml
├─ src/
│  ├─ extract/
│  │  └─ coingecko.py
│  ├─ load/
│  │  └─ postgres_loader.py
│  └─ utils/
│     └─ config.py            # local config (should be ignored)
└─ README.md
```

---

## Prerequisites

- Docker Desktop
- Docker Compose (v2)
- (Windows) WSL2 recommended

---

## Setup

### 1) Clone the repository

```bash
git clone <YOUR_REPO_URL>
cd e2e-data-pipeline-coingecko
```

### 2) Configure environment variables

**Recommended**: store secrets locally in an `.env` file (and do NOT commit it).

Create `airflow/.env`:

```env
COINGECKO_API_KEY=CG-YOUR-KEY-HERE
```

> CoinGecko may require a header key depending on your plan.  
> This project uses an API key via request headers.

### 3) Start the stack (Airflow + Postgres)

The Docker Compose file lives inside `airflow/`.

```bash
cd airflow
docker compose up -d
```

### 4) Open Airflow UI

- URL: http://localhost:8080

If you created the user inside the container, use the same credentials you configured (example):

- Username: `admin`
- Password: `admin`

> If login fails, create the user manually (see “Troubleshooting”).

---

## Running the pipeline

### Option A — Trigger manually (recommended for first run)

In Airflow:
1. Open DAG `coingecko_e2e_daily`
2. Toggle ON (unpause)
3. Click **Trigger DAG**
4. Confirm task succeeds (Logs → no errors)

### Option B — Scheduled run

The DAG is configured to run daily using a cron schedule (see the DAG file).

---

## Validate data in Postgres

### Count total rows

```bash
cd airflow
docker compose exec postgres psql -U airflow -d airflow -c "SELECT COUNT(*) FROM raw_coingecko_market_snapshot;"
```

### Check rows per snapshot (each run)

```bash
docker compose exec postgres psql -U airflow -d airflow -c "SELECT snapshot_ts, COUNT(*) AS rows
 FROM raw_coingecko_market_snapshot
 GROUP BY snapshot_ts
 ORDER BY snapshot_ts DESC
 LIMIT 10;"
```

### View latest inserted records

```bash
docker compose exec postgres psql -U airflow -d airflow -c "SELECT snapshot_ts, asset_id, symbol, current_price, market_cap_rank
 FROM raw_coingecko_market_snapshot
 ORDER BY snapshot_ts DESC, market_cap_rank ASC
 LIMIT 20;"
```

---

## Configuration notes

### Where the code runs
- DAGs are mounted into the Airflow container at: `/opt/airflow/dags`
- The `src/` folder is mounted into the Airflow container at: `/opt/airflow/src`

This allows the DAG to import your Python code directly.

### API key
The extractor sends the API key in request headers (example header key used in code):
- `x-cg-demo-api-key` (CoinGecko demo header)

---

## Troubleshooting

### 1) `no configuration file provided: not found`
You are running `docker compose` from the wrong folder.

Fix:
```bash
cd airflow
docker compose up -d
```

### 2) Airflow login invalid
Create the user manually inside the webserver container:

```bash
cd airflow
docker compose exec airflow-webserver airflow users create   --username admin   --password admin   --firstname YourName   --lastname YourLastName   --role Admin   --email you@example.com
```

### 3) DAG not appearing
- Confirm the file exists: `airflow/dags/coingecko_e2e_daily.py`
- Restart scheduler/webserver:

```bash
cd airflow
docker compose restart airflow-scheduler airflow-webserver
```

### 4) Import errors (`ModuleNotFoundError: No module named 'src'`)
This usually happens when the Python path/mount is wrong. Ensure your compose mounts `../src:/opt/airflow/src`
and the DAG imports match that structure.

---

## Next improvements (roadmap)

- Add a **transform** step (e.g., top movers 24h, volatility metrics)
- Create an **analytics schema** and incremental models (dbt or SQL tasks)
- Add **data quality checks** (row count, null checks, schema checks)
- Store snapshots partitioned by date for easier querying
- Add CI (lint, unit tests, pre-commit hooks)

---

## Disclaimer

This project is for learning and portfolio purposes. CoinGecko APIs have usage limits and may change behavior depending on your plan and authentication method.
