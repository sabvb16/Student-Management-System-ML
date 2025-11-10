import mysql.connector
from db_config import DB_CONFIG


# ✅ Function to add student
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


# ✅ Function to view all students
def view_students():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = "SELECT roll, name, class, email, phone, address, age, gpa FROM students"
        cursor.execute(query)

        rows = cursor.fetchall()

        if not rows:
            print("⚠️ No students found.")
            return

        print("\n📋 Student Records:")
        print("-" * 50)
        for row in rows:
            print(f"Roll: {row[0]}")
            print(f"Name: {row[1]}")
            print(f"Class: {row[2]}")
            print(f"Email: {row[3]}")
            print(f"Phone: {row[4]}")
            print(f"Address: {row[5]}")
            print(f"Age: {row[6]}")
            print(f"GPA: {row[7]}")
            print("-" * 50)

    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# ✅ Example usage (you can comment/uncomment as needed)
if __name__ == "__main__":
    # Add a sample student
    add_student("101", "Payal Sharma", "10th", "payal@example.com", "9876543210", "Mumbai")

    # View all students
    view_students()
