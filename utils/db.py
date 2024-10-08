import sqlite3 as sq

def get_connection():
    return sq.connect("database.db")

def execute_query(query, *params):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        conn.commit()
        cursor.close()
        return result

def add_user(user_id, first_name, username, phone_number):
    query = "INSERT OR IGNORE INTO info (user_id, first_name, username, phone_number) VALUES (?, ?, ?, ?)"
    return execute_query(query, user_id, first_name, username, phone_number)