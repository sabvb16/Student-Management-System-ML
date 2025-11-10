import mysql.connector
from db_config import DB_CONFIG

def update_student(roll, new_email=None, new_phone=None, new_address=None):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        updates = []
        values = []

        if new_email:
            updates.append("email = %s")
            values.append(new_email)
        if new_phone:
            updates.append("phone = %s")
            values.append(new_phone)
        if new_address:
            updates.append("address = %s")
            values.append(new_address)

        if not updates:
            print("⚠️ Nothing to update!")
            return

        query = f"UPDATE students SET {', '.join(updates)} WHERE roll = %s"
        values.append(roll)

        cursor.execute(query, tuple(values))
        conn.commit()

        if cursor.rowcount > 0:
            print("✅ Student details updated successfully!")
        else:
            print("⚠️ Student not found!")

    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Example usage
update_student("R001", new_email="alice_new@example.com", new_phone="9999999999")
