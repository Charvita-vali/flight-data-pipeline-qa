import pandas as pd
import pytest

CSV = "flight_details.csv"

EXPECTED_COLUMNS = {
    "flight_number", "airline", "dep_delay",
    "arr_delay", "flight_status", "checked_at",
}
VALID_STATUSES = {
    "active", "scheduled", "landed",
    "cancelled", "incident", "diverted",
}


@pytest.fixture
def df():
    return pd.read_csv(CSV)


def test_schema_has_expected_columns(df):
    missing = EXPECTED_COLUMNS - set(df.columns)
    assert not missing, f"Missing expected columns: {missing}"


def test_file_is_not_empty(df):
    assert len(df) > 0, "flight_details.csv is empty"


def test_flight_number_not_blank(df):
    blank = df[
        df["flight_number"].isna()
        | (df["flight_number"].astype(str).str.strip() == "")
    ]
    assert blank.empty, f"Found {len(blank)} flight(s) with a blank flight_number"


def test_flight_status_is_valid(df):
    bad = set(df["flight_status"].dropna().unique()) - VALID_STATUSES
    assert not bad, f"Unexpected flight_status values: {bad}"


def test_dep_delay_not_negative(df):
    negative = df[df["dep_delay"].notna() & (df["dep_delay"] < 0)]
    assert negative.empty, f"Found {len(negative)} flight(s) with a negative dep_delay"
