"""
poller/main.py — GBFS Station Status Poller

What this does:
    Fetches a live snapshot of all CitiBike station availability from the
    GBFS station_status API and batch loads it into BigQuery.

What it is NOT:
    This is not trip data. It captures real-time station state — how many
    bikes and docks are available at each station right now. The CitiBike
    app uses this same feed to show live availability to riders.

Data source:
    GBFS station_status API — returns one JSON snapshot of all 2508 stations.
    Each station reports bikes available, docks available, e-bike count,
    and operational status (installed, renting, returning).

Two timestamps per row:
    - snapshot_time: when CitiBike's system last updated the data (from the API)
    - fetched_at:    when this poller actually made the HTTP request (our clock)
    These differ because the API snapshot may be stale by seconds when we poll it.

Ingestion pattern:
    Uses load_table_from_json (batch load) not insert_rows_json (streaming).
    Batch loads are free tier. Streaming inserts cost money and are unnecessary
    at a 2-minute polling interval where a few seconds of latency is irrelevant.

Destination:
    nyc-transit-data-platform.citibike_live.station_status

Invoked by:
    Cloud Scheduler → Cloud Run job (every 2 minutes in production)
    Can also be run locally: python poller/main.py
"""

import requests
from google.cloud import bigquery
from datetime import datetime, timezone

PROJECT_ID = "nyc-transit-data-platform"
DATASET_ID = "citibike_live"
TABLE_ID = "station_status"

GBFS_URL = "https://gbfs.citibikenyc.com/gbfs/en/station_status.json"


def poll_and_load():
    # Fetch
    response = requests.get(GBFS_URL, timeout=10)
    response.raise_for_status()
    payload = response.json()

    #snapshot_time — when CitiBike's system last updated the station data (comes from the API itself).
    # fetched_at — when your poller actually went and grabbed it (recorded by your code).
    # Extract timestamps
    snapshot_time = datetime.fromtimestamp(payload["last_updated"], tz=timezone.utc)
    fetched_at = datetime.now(tz=timezone.utc)

    # Flatten stations
    rows = []
    #payload["data"]["stations"] you're just navigating inside the JSON structure
    for station in payload["data"]["stations"]:
        rows.append({
            "station_id": station["station_id"],
            "legacy_id": station.get("legacy_id"),
            "num_bikes_available": station["num_bikes_available"],
            "num_bikes_disabled": station["num_bikes_disabled"],
            "num_ebikes_available": station["num_ebikes_available"],
            "num_docks_available": station["num_docks_available"],
            "num_docks_disabled": station["num_docks_disabled"],
            "is_installed": station["is_installed"],
            "is_renting": station["is_renting"],
            "is_returning": station["is_returning"],
            "last_reported": station["last_reported"],
            "eightd_has_available_keys": station.get("eightd_has_available_keys"),
            "snapshot_time": snapshot_time.isoformat(),
            "fetched_at": fetched_at.isoformat(),
        })

    # Batch load into BigQuery
    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    job = client.load_table_from_json(rows, table_ref)
    job.result()  # Wait for completion

    print(f"Loaded {len(rows)} rows at {fetched_at.isoformat()}")


if __name__ == "__main__":
    poll_and_load()