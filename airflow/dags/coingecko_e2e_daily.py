from __future__ import annotations

from datetime import datetime, timedelta
import os

from airflow import DAG
from airflow.operators.python import PythonOperator

def extract_and_load(**context):
    from src.extract.coingecko import fetch_market_snapshot
    from src.load.postgres_loader import load_market_snapshot

    snapshot_ts = context["ts"]  # string ISO do Airflow
    rows = fetch_market_snapshot(vs_currency="usd", per_page=50, page=1)
    return load_market_snapshot(rows, snapshot_ts=snapshot_ts)



with DAG(
    dag_id = "coingecko_e2e_daily",
    description = "Extract coingecko /coins/market and Load into Postgres (RAW)",
    default_args = {"retries": 2, "retry_delay": timedelta(minutes=5)},
    start_date = datetime(2026, 1, 1),
    schedule="0 2 * * *",
    catchup =False,
    tags = ["coingecko", "e2e", "raw"],
) as dag:

    run_pipeline = PythonOperator(
PythonOperator(
    task_id="extract_and_load_market_snapshot",
    python_callable=extract_and_load,
)

    )