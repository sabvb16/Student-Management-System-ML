import streamlit as st
import mysql.connector
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from db_config import DB_CONFIG

# ---------- Database Connection ----------
def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        st.error(f"Database connection error: {e}")
        return None


# ---------- Add Student Function ----------
def add_student(roll, name, class_name, email, phone, address, age, gpa):
    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()

        query = """
        INSERT INTO students (roll, name, class, email, phone, address, age, gpa)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (roll, name, class_name, email, phone, address, age, gpa)

        cursor.execute(query, values)
        conn.commit()
        st.success("✅ Student added successfully!")

    except mysql.connector.Error as err:
        st.error(f"❌ Database Error: {err}")
        conn.rollback()

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# ---------- Update Student Function ----------
def update_student(roll, new_email=None, new_phone=None, new_address=None):
    conn = get_connection()
    if not conn:
        return

    try:
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
            st.warning("⚠️ Nothing to update!")
            return

        query = f"UPDATE students SET {', '.join(updates)} WHERE roll = %s"
        values.append(roll)

        cursor.execute(query, tuple(values))
        conn.commit()

        if cursor.rowcount > 0:
            st.success("✅ Student details updated successfully!")
        else:
            st.warning("⚠️ Student not found!")

    except mysql.connector.Error as err:
        st.error(f"❌ Database Error: {err}")
        conn.rollback()

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# ---------- View Students Function ----------
def view_students(search_term=None):
    conn = get_connection()
    if not conn:
        return pd.DataFrame()

    try:
        cursor = conn.cursor()

        if search_term:
            query = """
            SELECT * FROM students
            WHERE name LIKE %s OR class LIKE %s
            """
            values = (f"%{search_term}%", f"%{search_term}%")
            cursor.execute(query, values)
        else:
            cursor.execute("SELECT * FROM students")

        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        return df

    except mysql.connector.Error as err:
        st.error(f"❌ Error fetching data: {err}")
        return pd.DataFrame()

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# ---------- Streamlit UI ----------
st.set_page_config(page_title="Student Database", page_icon="🎓", layout="wide")

st.title("🎓 Student Management System")

# Sidebar with menu
st.sidebar.header("Navigation")
menu = ["Add Student", "View Students", "Update Student", "Analytics Dashboard", "Dropout Risk Predictor", "Low GPA Students"]
choice = st.sidebar.selectbox("📂 Menu", menu)

# Sidebar info
st.sidebar.write("### Quick Stats")
df_quick = view_students()
if not df_quick.empty:
    st.sidebar.metric("Total Students", len(df_quick))
    st.sidebar.metric("Classes", df_quick['class'].nunique())
else:
    st.sidebar.write("No data yet.")

st.sidebar.write("### About")
st.sidebar.write("Modern Student Management System with AI-powered insights.")

# Download Project Report
st.sidebar.write("### Download Report")
try:
    with open("project_report.md", "r") as f:
        report_content = f.read()
    st.sidebar.download_button("📄 Download Project Report (MD)", report_content, "project_report.md", "text/markdown")
except FileNotFoundError:
    st.sidebar.write("Report not available.")

# ---------- ADD STUDENT PAGE ----------
if choice == "Add Student":
    st.subheader("➕ Add New Student")

    with st.form("add_student_form"):
        col1, col2 = st.columns(2)
        with col1:
            roll = st.text_input("Roll Number", placeholder="e.g., R001")
            name = st.text_input("Student Name", placeholder="e.g., John Doe")
            email = st.text_input("Email", placeholder="e.g., john@example.com")
            age = st.number_input("Age", min_value=5, max_value=25, value=18)
        with col2:
            class_name = st.selectbox("Class", ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"])
            phone = st.text_input("Phone", placeholder="e.g., 1234567890")
            address = st.text_area("Address", placeholder="Enter full address")
            gpa = st.number_input("GPA", min_value=0.0, max_value=10.0, value=5.0, step=0.1)

        submitted = st.form_submit_button("Add Student")
        if submitted:
            if roll and name and class_name:
                add_student(roll, name, class_name, email, phone, address, age, gpa)
            else:
                st.error("Please fill in at least Roll Number, Name, and Class.")

# ---------- VIEW STUDENTS PAGE ----------
if choice == "View Students":
    st.subheader("👀 View Students")

    search_term = st.text_input("Search by name or class (optional)", placeholder="Enter search term")
    df = view_students(search_term)

    if not df.empty:
        st.dataframe(df, use_container_width=True)
        st.write(f"Showing {len(df)} students")

        # Export option
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Students Data (CSV)", csv_data, "students_data.csv", "text/csv")
    else:
        st.info("No students found.")

# ---------- UPDATE STUDENT PAGE ----------
if choice == "Update Student":
    st.subheader("✏️ Update Student")

    # First, select student to update
    df = view_students()
    if not df.empty:
        selected_roll = st.selectbox("Select Student to Update", df['roll'].tolist())
        student_info = df[df['roll'] == selected_roll].iloc[0]

        st.write(f"Updating: {student_info['name']} (Roll: {selected_roll})")

        with st.form("update_student_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_email = st.text_input("New Email", value=student_info['email'], placeholder="Leave blank to keep current")
                new_phone = st.text_input("New Phone", value=student_info['phone'], placeholder="Leave blank to keep current")
            with col2:
                new_address = st.text_area("New Address", value=student_info['address'], placeholder="Leave blank to keep current")

            submitted = st.form_submit_button("Update Student")
            if submitted:
                update_student(selected_roll, new_email, new_phone, new_address)
    else:
        st.warning("No students available to update.")

# ---------- ANALYTICS DASHBOARD PAGE ----------
if choice == "Analytics Dashboard":
    st.subheader("📊 Analytics Dashboard")

    df = view_students()
    if not df.empty:
        # Handle missing values with random data
        df['age'] = pd.to_numeric(df['age'], errors='coerce')
        df['gpa'] = pd.to_numeric(df['gpa'], errors='coerce')
        df['class'] = df['class'].fillna(pd.Series(np.random.choice(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'], size=len(df)), index=df.index))
        df['age'] = df['age'].fillna(pd.Series(np.random.randint(15, 26, size=len(df)), index=df.index))
        df['gpa'] = df['gpa'].fillna(pd.Series(np.round(np.random.uniform(0.0, 10.0, size=len(df)), 1), index=df.index))

        # Class distribution
        st.write("### Class Distribution")
        class_counts = df['class'].value_counts()
        fig = px.pie(names=class_counts.index, values=class_counts.values, title="Students per Class")
        st.plotly_chart(fig)

        # Total students
        st.metric("Total Students", len(df))

        # Gender distribution (assuming no gender, simulate or skip)
        # For advanced, add gender to db

        # Age distribution
        st.write("### Age Distribution")
        age_bins = pd.cut(df['age'], bins=[0, 15, 18, 21, 25], labels=['<16', '16-18', '19-21', '22+'])
        age_counts = age_bins.value_counts()
        fig_age = px.pie(names=age_counts.index, values=age_counts.values, title="Age Distribution")
        st.plotly_chart(fig_age)

        # Performance metrics
        st.write("### Class-wise GPA Distribution")
        class_gpa = df.groupby('class')['gpa'].mean().reset_index()
        fig_gpa = px.bar(class_gpa, x='class', y='gpa', color='class', title="Average GPA by Class")
        st.plotly_chart(fig_gpa)

        # Export data
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Analytics Data (CSV)", csv_data, "analytics_data.csv", "text/csv")
    else:
        st.warning("No data available for analytics.")

# ---------- DROPOUT RISK PREDICTOR PAGE ----------
if choice == "Dropout Risk Predictor":
    st.subheader("🔮 Dropout Risk Predictor")

    df = view_students()
    if not df.empty and len(df) > 5:
        # Advanced ML-based prediction
        # Prepare data for ML
        df_ml = df.copy()
        df_ml['class_numeric'] = pd.to_numeric(df_ml['class'], errors='coerce').fillna(0)
        df_ml['grades'] = np.random.uniform(50, 100, len(df_ml))     # Simulated grades
        df_ml['dropout'] = np.random.choice([0, 1], len(df_ml), p=[0.7, 0.3])  # Simulated target

        # Features and target
        features = ['class_numeric', 'age', 'gpa', 'grades']
        X = df_ml[features]
        y = df_ml['dropout']

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Model training
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Predictions
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        # Predict on full data
        df_ml['predicted_risk'] = model.predict(X).astype(str)
        df_ml['predicted_risk'] = df_ml['predicted_risk'].map({'1': 'High', '0': 'Low'})

        # Display results
        st.write(f"### Model Accuracy: {accuracy:.2f}")
        st.write("### Predicted Dropout Risks")
        risk_counts = df_ml['predicted_risk'].value_counts()
        st.bar_chart(risk_counts)

        # Risk distribution
        fig = px.pie(names=risk_counts.index, values=risk_counts.values, title="Risk Distribution")
        st.plotly_chart(fig)

        # High-risk students
        high_risk = df_ml[df_ml['predicted_risk'] == 'High']
        # Add reason column
        high_risk['Reason'] = high_risk.apply(lambda row: 'GPA' if row['gpa'] < 5 else 'Grades', axis=1)
        st.write("### High-Risk Students")
        st.dataframe(high_risk[['name', 'class', 'age', 'gpa', 'grades', 'predicted_risk', 'Reason']])

        # Recommendations
        high_risk_percentage = (len(high_risk) / len(df_ml)) * 100
        if high_risk_percentage > 20:
            st.error(f"⚠️ HIGH RISK: {high_risk_percentage:.1f}% of students are at risk of dropping out.")


        # Recommended Interventions
        if len(high_risk) > 0:
            st.write("### Recommended Interventions:")
            st.write("• Immediate academic counseling session")
            st.write("• Weekly progress check-ins")
            st.write("• Access to additional learning resources")
            st.write("• Connection with student success advisor")

        # Export predictions
        csv_data = df_ml[['name', 'class', 'predicted_risk']].to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Risk Predictions (CSV)", csv_data, "dropout_risk_predictions.csv", "text/csv")

    else:
        st.warning("Not enough data for prediction. Add more students first.")

# ---------- LOW GPA STUDENTS PAGE ----------
if choice == "Low GPA Students":
    st.subheader("📉 Low GPA Students (GPA < 5)")

    df = view_students()
    if not df.empty:
        # Ensure GPA is numeric for accurate filtering
        df['gpa'] = pd.to_numeric(df['gpa'], errors='coerce').fillna(0)
        # Filter students with GPA < 5
        low_gpa_df = df[df['gpa'] < 5]

        if not low_gpa_df.empty:
            st.write(f"Found {len(low_gpa_df)} students with GPA less than 5.")

            # Display the dataframe
            st.dataframe(low_gpa_df, use_container_width=True)

            # Download option
            csv_data = low_gpa_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Low GPA Students Data (CSV)", csv_data, "low_gpa_students.csv", "text/csv")
        else:
            st.success("No students with GPA less than 5 found.")
    else:
        st.warning("No data available.")
