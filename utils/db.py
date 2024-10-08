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

def set_user_active(user_id):
    query = "UPDATE info SET activity = True WHERE user_id = ?"
    return execute_query(query, user_id)

def set_user_inactive(user_id):
    query = "UPDATE info SET activity = False WHERE user_id = ?"
    return execute_query(query, user_id)

def is_user_active(user_id):
    query = "SELECT activity FROM info WHERE user_id = ?"
    return execute_query(query, user_id)
    
def get_name(user_id):
    query = "SELECT name FROM info WHERE user_id = ?"
    return execute_query(query, user_id)

def get_first_name(user_id):
    query = "SELECT first_name FROM info WHERE user_id = ?"
    return execute_query(query, user_id)

def save_name(name, user_id):
    query = "UPDATE info SET name = ? WHERE user_id = ?"
    return execute_query(query, name, user_id)