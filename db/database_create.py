import sqlite3

# Connect to database
con = sqlite3.connect("wether.db")

# Create a cursor
cur = con.cursor()

# Load and run script
script = open("database_create_script.sql").read()
cur.executescript(script)

# Save changes
con.commit()
