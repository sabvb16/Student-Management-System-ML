import mysql.connector
from mysql.connector import Error
from db_config import DB_CONFIG

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    if conn.is_connected():
        print("✅ Connection successful!")
except Error as e:
    print(f"❌ Error: {e}")
finally:
    if 'conn' in locals() and conn.is_connected():
        conn.close()
