import mysql.connector
from db_config import DB_CONFIG

def delete_student(roll):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = "DELETE FROM students WHERE roll = %s"
        cursor.execute(query, (roll,))
        conn.commit()

        if cursor.rowcount > 0:
            print("🗑️ Student deleted successfully!")
        else:
            print("⚠️ Student not found!")

    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Example usage
delete_student("R001")
