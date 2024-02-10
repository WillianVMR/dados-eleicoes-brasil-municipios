import sqlite3
import csv

# Connect to your SQLite database
conn = sqlite3.connect('geolocalizacao_sp.sqlite3')
cursor = conn.cursor()

# Query the table
cursor.execute('SELECT * FROM dataset_capital')
data = cursor.fetchall()

# Specify the CSV file you want to output
with open('eleitorado_local_votacao_2012.csv', 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    # Write the headers (optional)
    csv_writer.writerow([i[0] for i in cursor.description])
    # Write the data
    csv_writer.writerows(data)

# Close the SQLite connection
conn.close()
