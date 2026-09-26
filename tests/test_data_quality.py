"""
Data quality tests for the flight ETL pipeline.
Validates the data that etl.py loaded into flights.db.
Run with: pytest -v
"""
import sqlite3
import pandas as pd
import pytest

DB = "flights.db"
TABLE = "flight_snapshots"

EXPECTED_COLUMNS = {
    "id", "flight_number", "airline", "dep_airport", "arr_airport",
    "dep_scheduled", "dep_delay", "arr_scheduled", "arr_delay",
    "flight_status", "checked_at",
}
VALID_STATUSES = {"active", "scheduled", "landed", "cancelled", "incident", "diverted"}


@pytest.fixture
def df():
    """Load the whole flight_snapshots table into a DataFrame once."""
    conn = sqlite3.connect(DB)
    data = pd.read_sql_query(f"SELECT * FROM {TABLE}", conn)
    conn.close()
    return data


def test_schema_has_expected_columns(df):
    """The table should contain every column the pipeline promises."""
    missing = EXPECTED_COLUMNS - set(df.columns)
    assert not missing, f"Missing expected columns: {missing}"


def test_table_is_not_empty(df):
    """A successful ETL run should load at least one flight."""
    assert len(df) > 0, "flight_snapshots is empty — did etl.py run?"


def test_flight_number_not_blank(df):
    """
    Every flight should have a flight number.
    NOTE: this catches a real data-quality issue in the source feed —
    some API records arrive with a blank flight number and airline 'empty'.
    """
    blank = df[df["flight_number"].isna() | (df["flight_number"].astype(str).str.strip() == "")]
    assert blank.empty, f"Found {len(blank)} flights with a blank flight_number"


def test_flight_status_is_valid(df):
    """flight_status must be one of the known API values."""
    bad = set(df["flight_status"].dropna().unique()) - VALID_STATUSES
    assert not bad, f"Unexpected flight_status values: {bad}"


def test_delays_are_not_negative(df):
    """A departure delay in minutes should never be negative."""
    negative = df[df["dep_delay"].notna() & (df["dep_delay"] < 0)]
    assert negative.empty, f"Found {len(negative)} flights with a negative dep_delay"


def test_csv_matches_database(df):
    """The exported CSV should have the same number of rows as the database."""
    csv = pd.read_csv("flight_details.csv")
    assert len(csv) == len(df), (
        f"Row mismatch: DB has {len(df)}, CSV has {len(csv)}"
    )
