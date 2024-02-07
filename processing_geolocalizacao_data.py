import pandas as pd
import sqlite3
import threading
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Connect to the SQLite database
conn = sqlite3.connect('geolocalizacao_sp.sqlite3')
cursor = conn.cursor()

# Initialize the geocoder with a custom timeout (e.g., 10 seconds)
geolocator = Nominatim(user_agent="geoapiExercises", timeout=10)

# Adjust the rate limiter to wait longer between requests, e.g., 2 seconds between requests
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=2, error_wait_seconds=10, max_retries=2, swallow_exceptions=False)

def geocode_address(address):
    try:
        location = geocode(address)
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        print(f"Error geocoding {address}: {e}")
        return None, None

# Flag to control the updating process
stop_requested = False

def check_for_stop():
    global stop_requested
    while not stop_requested:
        user_input = input('Digite "stop" para encerrar:\n')
        if user_input == 'stop':
            stop_requested = True
            print("Stop requested. Finishing up...")

# Start the stop checking in a separate thread
stop_thread = threading.Thread(target=check_for_stop)
stop_thread.start()

# Function to update rows
def update_rows():
    rows_updated = 0
    total_rows = cursor.execute("SELECT COUNT(*) FROM dataset_capital WHERE GEOCODED = 0").fetchone()[0]
    if total_rows == 0:
        print("All rows have already been geocoded.")
        return

    for row in cursor.execute("SELECT rowid, FORMATADO_COM_DS_ENDERECO FROM dataset_capital WHERE GEOCODED = 0").fetchall():
        if stop_requested:
            break
        rowid, address = row
        latitude, longitude = geocode_address(address)
        if latitude and longitude:
            cursor.execute("UPDATE dataset_capital SET NEW_NR_LATITUDE = ?, NEW_NR_LONGITUDE = ?, GEOCODED = 1 WHERE rowid = ?", (latitude, longitude, rowid))
            conn.commit()
            rows_updated += 1
            print(f"Updated row {rowid}. {rows_updated}/{total_rows} ({(rows_updated/total_rows)*100:.2f}%)")
    
    print(f"Total rows updated: {rows_updated}/{total_rows} ({(rows_updated/total_rows)*100:.2f}%)")

# Call the update function
update_rows()

# Close the database connection
conn.close()

# Wait for the stop thread to finish
stop_thread.join()
