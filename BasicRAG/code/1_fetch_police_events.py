import psycopg
import os
from dotenv import load_dotenv
import json
import requests

load_dotenv()

# url = "https://polisen.se/api/events"

headers = {
    "User-agent" : "your-agent" # For transparency
}

# response = requests.get(url=url, headers=headers)

# json_data = json.dumps(response.json(), indent=4)
# with open("police_events.json", "w") as f:
#     f.write(json_data)
#     f.close()



# # Try connecting to the default 'postgres' database instead of 'events_db'
with open("../police_events.json") as f:
    data = json.load(f)  # this is your list of dicts

print("Connecting...")

conn = psycopg.connect(
    host="localhost",
    port=5432,
    user="postgres",
    password="testpassword123",
    dbname="events_db",
)
cur = conn.cursor()


print("Creating or checking table...")
# Recommended table (note: gps split into lat/lon)
cur.execute("""
    CREATE TABLE IF NOT EXISTS events_db(
        id bigint PRIMARY KEY,
        title varchar(256),
        date timestamptz,
        summary varchar(256),
        url varchar(256),
        type varchar(256),
        lat float,
        lon float
    )
""")
conn.commit()

insert_query = """
    INSERT INTO events_db(id, title, date, summary, url, type, lat, lon)
    VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id) DO NOTHING
"""

rows = []
for item in data:
    gps = item.get("location", {}).get("gps", "")
    lat, lon = (gps.split(",") + [None, None])[:2] if gps else (None, None)
    rows.append((
        item["id"],
        item["name"],
        item["datetime"],
        item["summary"],
        item["url"],
        item["type"],
        float(lat) if lat else None,
        float(lon) if lon else None,
    ))

cur.executemany(insert_query, rows)
conn.commit()

print(f"✓ Inserted {len(rows)} rows")

cur.close()
conn.close()

cur.close()