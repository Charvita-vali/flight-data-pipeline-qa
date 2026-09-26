import sqlite3
from datetime import datetime
from api_client import get_flights

def save_flights(dep_iata, arr_iata):
    data = get_flights(dep_iata=dep_iata, arr_iata=arr_iata)

    conn = sqlite3.connect("flights.db")
    cur = conn.cursor()

    flights = data.get("data", [])

    for f in flights:
        flight_number = f.get("flight", {}).get("iata")
        airline = f.get("airline", {}).get("name")
        if not flight_number:
            continue
        dep_airport = f.get("departure", {}).get("airport")
        arr_airport = f.get("arrival", {}).get("airport")
        dep_scheduled = f.get("departure", {}).get("scheduled")
        dep_delay = f.get("departure", {}).get("delay")
        arr_scheduled = f.get("arrival", {}).get("scheduled")
        arr_delay = f.get("arrival", {}).get("delay")
        status = f.get("flight_status")

        cur.execute("""
            INSERT INTO flight_snapshots
            (flight_number, airline, dep_airport, arr_airport, dep_scheduled, dep_delay, arr_scheduled, arr_delay, flight_status, checked_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (flight_number, airline, dep_airport, arr_airport, dep_scheduled, dep_delay, arr_scheduled, arr_delay, status, datetime.now().isoformat()))

    conn.commit()
    conn.close()
    print(f"Saved {len(flights)} flight records for {dep_iata} -> {arr_iata}")

if __name__ == "__main__":
    save_flights("MIA", "JFK")
