import os
import psycopg2
from psycopg2.extras import execute_values

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS raw_coingecko_market_snapshot (
  snapshot_ts timestamptz NOT NULL,
  asset_id text NOT NULL,
  symbol text,
  name text,
  current_price double precision,
  market_cap double precision,
  market_cap_rank integer,
  total_volume double precision,
  high_24h double precision,
  low_24h double precision,
  price_change_24h double precision,
  price_change_percentage_24h double precision,
  last_updated timestamptz,
  PRIMARY KEY (snapshot_ts, asset_id)
);
"""

INSERT_SQL = """
INSERT INTO raw_coingecko_market_snapshot (
  snapshot_ts, asset_id, symbol, name, current_price, market_cap, market_cap_rank,
  total_volume, high_24h, low_24h, price_change_24h, price_change_percentage_24h, last_updated
) VALUES %s
ON CONFLICT (snapshot_ts, asset_id) DO UPDATE SET
  symbol = EXCLUDED.symbol,
  name = EXCLUDED.name,
  current_price = EXCLUDED.current_price,
  market_cap = EXCLUDED.market_cap,
  market_cap_rank = EXCLUDED.market_cap_rank,
  total_volume = EXCLUDED.total_volume,
  high_24h = EXCLUDED.high_24h,
  low_24h = EXCLUDED.low_24h,
  price_change_24h = EXCLUDED.price_change_24h,
  price_change_percentage_24h = EXCLUDED.price_change_percentage_24h,
  last_updated = EXCLUDED.last_updated;
"""
def get_conn():
    db_url = os.getenv("POSTGRES_URL")
    if not db_url:
        raise RuntimeError("Sem URL")
    return psycopg2.connect(db_url)


def load_market_snapshot(rows: list[dict]) -> int:
  if not rows:
    return 0

  values = [(
    r["snapshot_ts"],
    r["asset_id"],
    r["symbol"],
    r["name"],
    r["current_price"],
    r["market_cap"],
    r["market_cap_rank"],
    r["total_volume"],
    r["high_24h"],
    r["low_24h"],
    r["price_change_24h"],
    r["price_change_percentage_24h"],
    r["last_updated"]
  )
  for r in rows
  ]

  with get_conn() as conn:
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLE_SQL)      # <-- AQUI você “insere” o SQL
        execute_values(cur, INSERT_SQL, values, page_size=1000)
    conn.commit()

  return len(values)