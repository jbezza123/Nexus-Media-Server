import sqlite3

connection = sqlite3.connect('../db/server_log.db')
cursor = connection.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS log_entries (
        ip_address TEXT PRIMARY KEY,
        timestamp TEXT,
        user_agent TEXT
    )
''')
connection.commit()
connection.close()

# Connect to the SQLite database
connection = sqlite3.connect('../db/auth_cookies.db')
cursor = connection.cursor()

# Create the 'cookies' table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS cookies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        value TEXT,
        ip_address TEXT,
        user_agent TEXT
    )
''')

# Commit the changes and close the connection
connection.commit()
connection.close()
