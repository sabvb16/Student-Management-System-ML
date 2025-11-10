import mysql.connector
from db_config import DB_CONFIG

def add_student(roll, name, class_name, email, phone, address):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = """
        INSERT INTO students (roll, name, class, email, phone, address)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (roll, name, class_name, email, phone, address)

        cursor.execute(query, values)
        conn.commit()

        print("✅ Student added successfully!")

    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Example usage
add_student("R001", "Alice", "10A", "alice@example.com", "9876543210", "Pune")
