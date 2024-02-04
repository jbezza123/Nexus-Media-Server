from flask import request, abort
from datetime import datetime, timedelta
import uuid
import json
from json.decoder import JSONDecodeError
import sqlite3
import configparser

config = configparser.ConfigParser()
config.read('config.cfg')

# Read security-related configurations
user_agents_file = config.get('SECURITY', 'USER_AGENTS_FILE')#txt file 1
log_db_file = config.get('SECURITY', 'LOG_DB_FILE')#db file
bad_log_file = config.get('SECURITY', 'BAD_LOG_FILE')#txt file 2
log_file = config.get('SECURITY', 'LOG_FILE')#txt file 3

# Read user agents from a file into a list when the script is first run
try:
    with open(user_agents_file, 'r') as file:
        user_agents_list = [line.strip() for line in file]
except FileNotFoundError:
    user_agents_list = []  # If the file is not found, initialize an empty list

def remove_old_cookies(db_file):
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Calculate the datetime 8 hours ago
        eight_hours_ago = datetime.now() - timedelta(hours=8)
        eight_hours_ago_str = eight_hours_ago.strftime("%Y-%m-%d %H:%M:%S")

        # Remove cookies older than 8 hours
        cursor.execute('''
            DELETE FROM cookies
            WHERE timestamp < ?
        ''', (eight_hours_ago_str,))

        conn.commit()
    except Exception as e:
        print(f"Error removing old cookies: {e}")
    finally:
        conn.close()
        
def block_bad_connections():
    ip_address = request.remote_addr
    user_agent = request.user_agent.string

    # Example: Block connections with a specific user agent
    if 'bad_user_agent' in user_agent:
        log_bad_connection(ip_address, user_agent)
        abort(400)
        
    if any(agent in user_agent for agent in user_agents_list):
        log_bad_connection(ip_address, user_agent)
        abort(400)
        
    if '' in user_agent:
        log_connection(ip_address, user_agent)

def log_bad_connection(ip_address, user_agent):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - Bad Connection Blocked: IP={ip_address}, User-Agent={user_agent}\n"

    with open(bad_log_file, 'a') as log_file:
        log_file.write(log_entry)
        
def log_connection(ip_address, user_agent):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    connection = sqlite3.connect(log_db_file)
    cursor = connection.cursor()

    try:
        # Try to update the existing entry
        cursor.execute('''
            UPDATE log_entries
            SET timestamp = ?, user_agent = ?
            WHERE ip_address = ?
        ''', (timestamp, user_agent, ip_address))
        
        if cursor.rowcount == 0:
            # If no rows were updated, insert a new entry
            cursor.execute('''
                INSERT INTO log_entries (ip_address, timestamp, user_agent)
                VALUES (?, ?, ?)
            ''', (ip_address, timestamp, user_agent))

        connection.commit()
    except Exception as e:
        print(f"Error logging connection: {e}")
    finally:
        connection.close()

        
def log_event(event_type, details):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - {event_type}: {details}\n"

    with open(log_file, 'a') as log_file:
        log_file.write(log_entry)

def is_authenticated(request, db_file):
    ip_address = request.remote_addr
    user_agent = request.user_agent.string
    cookie_value = request.cookies.get('auth_cookie')

    if cookie_value is not None:
        return validate_cookie(cookie_value, db_file)

    return False

def validate_cookie(cookie_value, db_file):
    remove_old_cookies(db_file)
    ip_address = request.remote_addr
    user_agent = request.user_agent.string

    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Check if the provided cookie, IP, and user agent match any entry in the database
    cursor.execute('''
        SELECT COUNT(*)
        FROM cookies
        WHERE value = ? AND ip_address = ? AND user_agent = ?
    ''', (cookie_value, ip_address, user_agent))

    count = cursor.fetchone()[0]

    # Close the connection
    conn.close()

    return count > 0
def generate_cookie(db_file):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip_address = request.remote_addr
    user_agent = request.user_agent.string
    new_cookie = '-'.join(str(uuid.uuid4()) for _ in range(5))

    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Insert the new cookie into the database
    cursor.execute('''
        INSERT INTO cookies (timestamp, value, ip_address, user_agent)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, new_cookie, ip_address, user_agent))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    return new_cookie
