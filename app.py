import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime

# ---------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------

st.set_page_config(
    page_title="School Management Analytics System",
    layout="wide",
    page_icon="🎓"
)

# ---------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------

conn = sqlite3.connect('school.db', check_same_thread=False)
cursor = conn.cursor()

# ---------------------------------------------------
# CREATE TABLES
# ---------------------------------------------------

cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    class_name TEXT,
    math INTEGER,
    science INTEGER,
    english INTEGER,
    computer INTEGER,
    physics INTEGER,
    economic INTEGER,
    education INTEGER,
    biology INTEGER,
    attendance REAL,
    total INTEGER,
average REAL,
    grade TEXT,
    status TEXT,
    created_at TEXT
)
''')

conn.commit()

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.title("🎓 School Analytics System")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Upload Results",
        "Student Analytics",
        "Attendance Analytics",
        "Reports",
        "Database Records"
    ]
)

# ---------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------

def classify(avg):
    if avg >= 90:
        return 'A+', 'Excellent'
    elif avg >= 75:
        return 'A', 'Distinction'
    elif avg >= 60:
        return 'B', 'First Class'
    elif avg >= 40:
        return 'C', 'Pass'
    else:
        return 'F', 'Fail'

    # ---------------------------------------------------
    # DASHBOARD
    # ---------------------------------------------------

if menu == "Dashboard":

        st.title("📊 School Management Dashboard")

        data = pd.read_sql_query("SELECT * FROM students", conn)

        if len(data) > 0:
            total_students = len(data)
            avg_score = round(data['average'].mean(), 2)
            topper = data['total'].max()
            pass_rate = round((len(data[data['status'] != 'Fail']) / total_students) * 100, 2)

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Total Students", total_students)
            col2.metric("Average Score", avg_score)
            col3.metric("Top Score", topper)
            col4.metric("Pass Rate", f"{pass_rate}%")

            st.subheader("Student Status Distribution")

            status_chart = data['status'].value_counts().reset_index()
            status_chart.columns = ['Status', 'Count']

            fig1 = px.pie(
                status_chart,
                names='Status',
                values='Count',
                title='Performance Classification'
            )

            st.plotly_chart(fig1, use_container_width=True)

            st.subheader("Class Performance")

            class_chart = data.groupby('class_name')['average'].mean().reset_index()

            fig2 = px.bar(
                class_chart,
                x='class_name',
                y='average',
                title='Average Performance by Class'
            )

            st.plotly_chart(fig2, use_container_width=True)

        else:
            st.warning("No student records available.")

   # ---------------------------------------------------
   # UPLOAD RESULTS
   # ---------------------------------------------------

elif menu == "Upload Results":

        st.title("📂 Upload Student Result Sheet")

        uploaded_file = st.file_uploader(
            "Upload CSV or Excel File",
            type=['csv', 'xlsx']
        )

        if uploaded_file is not None:

            # Read file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

                st.subheader("Uploaded Dataset")
                st.dataframe(df)

                subjects = ['Math', 'Science', 'English', 'Computer']

                # Calculate totals
                df['Total'] = df[subjects].sum(axis=1)
                df['Average'] = df[subjects].mean(axis=1)

                grades = []
                status_list = []

                for avg in df['Average']:
                    grade, status = classify(avg)
                    grades.append(grade)
                    status_list.append(status)

                df['Grade'] = grades
                df['Status'] = status_list

                # Ranking
                df['Rank'] = df['Total'].rank(ascending=False)
                st.subheader("Processed Results")
                st.dataframe(df)

                # Save data
                if st.button("Save to Database"):

                    for _, row in df.iterrows():
                        cursor.execute('''
                                INSERT INTO students (
                                    name, class_name, math, science,
                                    english, computer, physics, economic, education,biology, attendance,
                                    total, average, grade, status,
                                    created_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (
                            row['Name'],
                            row['Class'],
                            int(row['Math']),
                            int(row['Science']),
                            int(row['English']),
                            int(row['Computer']),
                            int(row['physics']),
                            int(row['economic']),
                            int(row['education']),
                            int(row['biology']),
                            float(row['Attendance']),
                            int(row['Total']),
                            float(row['Average']),
                            row['Grade'],
                            row['Status'],
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ))

                    conn.commit()

                    st.success("Data saved successfully!")

                # Download result
                csv = df.to_csv(index=False).encode('utf-8')

                st.download_button(
                    label="⬇ Download Processed Results",
                    data=csv,
                    file_name='processed_results.csv',
                    mime='text/csv'
                )

                # ---------------------------------------------------
                # STUDENT ANALYTICS
                # ---------------------------------------------------

        elif menu == "Student Analytics":

                st.title("📈 Student Analytics")

                data = pd.read_sql_query("SELECT * FROM students", conn)

                if len(data) > 0:
                    st.subheader("Top Performing Students")

                    top_students = data.sort_values(by='total', ascending=False).head(10)

                    fig3 = px.bar(
                        top_students,
                        x='name',
                        y='total',
                        title='Top 10 Students'
                    )

                    st.plotly_chart(fig3, use_container_width=True)

                    st.subheader("Subject-wise Performance")

                    subject_avg = {
                        'Math': data['math'].mean(),
                        'Science': data['science'].mean(),
                        'English': data['english'].mean(),
                        'Computer': data['computer'].mean(),
                        'phisics': data['physics'].mean(),
                        'economic': data['economic'].mean(),
                        'education': data['education'].mean(),
                        'biology': data['biology'].mean()
                    }

                    subject_df = pd.DataFrame({
                        'Subject': subject_avg.keys(),
                        'Average Score': subject_avg.values()
                    })

                    fig4 = px.bar(
                        subject_df,
                        x='Subject',
                        y='Average Score',
                        title='Average Subject Scores'
                    )

                    st.plotly_chart(fig4, use_container_width=True)

                    st.subheader("Student Search")

                    student_name = st.text_input("Enter Student Name")

                    if student_name:
                        result = data[data['name'].str.contains(student_name, case=False)]
                        st.dataframe(result)

                # ---------------------------------------------------
                # ATTENDANCE ANALYTICS
                # ---------------------------------------------------

        elif menu == "Attendance Analytics":
            st.title("📅 Attendance Analytics")

            data = pd.read_sql_query("SELECT * FROM students", conn)

            if len(data) > 0:
                fig5 = px.histogram(
                    data,
                    x='attendance',
                    title='Attendance Distribution'
                )

                st.plotly_chart(fig5, use_container_width=True)

                low_attendance = data[data['attendance'] < 50]

                st.subheader("Low Attendance Students")
                st.dataframe(low_attendance)

        # ---------------------------------------------------
        # REPORTS
        # ---------------------------------------------------

        elif menu == "Reports":

            st.title("📝 Reports Section")

            data = pd.read_sql_query("SELECT * FROM students", conn)

            if len(data) > 0:
                st.subheader("Complete Student Report")
                st.dataframe(data)

                csv = data.to_csv(index=False).encode('utf-8')

                st.download_button(
                    label="Download Full School Report",
                    data=csv,
                    file_name='school_report.csv',
                    mime='text/csv'
                )

            # ---------------------------------------------------
            # DATABASE RECORDS
            # ---------------------------------------------------

            elif menu == "Database Records":

                st.title("🗂 Database Records")

                data = pd.read_sql_query("SELECT * FROM students", conn)

                if len(data) > 0:
                    st.dataframe(data)
                else:
                    st.warning("Database is empty.")

            # ---------------------------------------------------
            # FOOTER
            # ---------------------------------------------------

            st.markdown("---")
            st.caption("School Management Analytics System | Developed with Streamlit & Python")
