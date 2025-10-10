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
    query = """
    INSERT INTO info (user_id, first_name, username, phone_number)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(user_id) DO UPDATE SET
        phone_number = CASE
            WHEN info.phone_number IS NULL OR info.phone_number = ''
            THEN excluded.phone_number
            ELSE info.phone_number
        END
    """
    return execute_query(query, user_id, first_name, username, phone_number)

def is_user_in_db(user_id):
    query = "SELECT COUNT(1) FROM info WHERE user_id = ?"
    result = execute_query(query, user_id)
    return result[0][0] > 0

def get_name(user_id):
    query = "SELECT name FROM info WHERE user_id = ?"
    return execute_query(query, user_id)

def get_first_name(user_id):
    query = "SELECT first_name FROM info WHERE user_id = ?"
    return execute_query(query, user_id)

def save_name(name, user_id):
    query = "UPDATE info SET name = ? WHERE user_id = ?"
    return execute_query(query, name, user_id)

def get_number(user_id):
    query = "SELECT phone_number FROM info WHERE user_id = ?"
    return execute_query(query, user_id)

# =====================================================================================
# ================================= User-activity =====================================
# =====================================================================================

def set_user_active(user_id):
    query = "UPDATE info SET activity = True WHERE user_id = ?"
    return execute_query(query, user_id)

def set_user_inactive(user_id):
    query = "UPDATE info SET activity = False WHERE user_id = ?"
    return execute_query(query, user_id)

def is_user_active(user_id):
    query = "SELECT activity FROM info WHERE user_id = ?"
    return execute_query(query, user_id)

# =====================================================================================
# ===================================== Ban ===========================================
# =====================================================================================

def set_user_banned(user_id):
    query = "UPDATE info SET ifbanned = True WHERE user_id = ?"
    return execute_query(query, user_id)

def set_user_unbanned(user_id):
    query = "UPDATE info SET ifbanned = False WHERE user_id = ?"
    return execute_query(query, user_id)

def is_user_banned(user_id):
    query = "SELECT ifbanned FROM info WHERE user_id = ?" 
    return execute_query(query, user_id)

def get_banned_users():
    query = "SELECT user_id, username FROM info WHERE ifbanned = True"
    return execute_query(query)

def get_unbanned_users():
    query = "SELECT user_id FROM info WHERE ifbanned = False"
    result = execute_query(query)
    return [row[0] for row in result] if result else []
