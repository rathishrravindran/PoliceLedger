"""
Police Ledger – Traffic Stop Monitoring Dashboard

Tech Stack:
- Python
- SQLite
- Pandas
- Streamlit

How it works:
- Cleans raw Excel data
- Loads data into SQLite (first run only)
- Runs SQL analytics
- Displays interactive charts using Streamlit
"""


import pandas as pd  # Data handling (Excel, CSV, DataFrames)
import openpyxl  # Required to read Excel (.xlsx) files
import streamlit as st # Web dashboard framework
import sqlite3 # Lightweight database (no password needed)
import os  # File system checks (to see if DB exists)

# ---------------------------------------------
# STEP 1: LOAD & CLEAN RAW EXCEL DATA
# ---------------------------------------------

# Load the Excel dataset
df = pd.read_excel("traffic_stops.xlsx", engine="openpyxl")

st.subheader("📋 Raw Data")

st.dataframe(df.head())

# 🔹 Remove columns that contain ONLY missing values
df = df.dropna(axis=1, how='all')


# 🔹 Replace NaN values
df = df.fillna({
    'driver_age': 0,
    'driver_gender': 'Unknown',
    'driver_race': 'Unknown',
    'violation': 'Unknown',
    'search_conducted': 'False',
    'search_type': 'None',
    'stop_outcome': 'Unknown',
    'is_arrested': 'False',
    'stop_duration': 'Unknown',
    'drugs_related_stop': 'False',
    'vehicle_number': 'Unknown'
})


# 🔹 Save cleaned data so we don't repeat cleaning every time

df.to_csv("cleaned_traffic_stops.csv", index=False)
print("Data cleaned and saved successfully!")

# ---------------------------------------------
# DATABASE CONFIGURATION (SQLite)
# ---------------------------------------------

SQLITE_DB = "traffic.db"

# -------------------------------------------------
# DB Connection
# -------------------------------------------------

def get_connection():
    return sqlite3.connect(SQLITE_DB)

print("Connected Successfully")

# ---------------------------------------------
# INITIALIZE SQLITE DATABASE (Auto Create DB) Creates the SQLite database and loads data ONLY ifthe database file does not already exist.
# ---------------------------------------------

def init_sqlite():
    if not os.path.exists(SQLITE_DB):
        conn = sqlite3.connect(SQLITE_DB)
        df = pd.read_csv("cleaned_traffic_stops.csv")
        df.to_sql("traffic_dat", conn, index=False, if_exists="replace")
        conn.close()

 # DB connection for the rest of the code

init_sqlite()
conn = get_connection()
cursor = conn.cursor()


# -------------------------------------------------
# PYTHON FILE TO DISPLAY STREAMLIT IN BROWSER WITH BAR CHART
# -------------------------------------------------

import matplotlib.pyplot as plt # For pie charts (Streamlit alone can’t do pie)


# -------------------------------------------------
# Chart Renderer
# -------------------------------------------------
def render_chart(analysis_option, df):
    if df.empty:
        st.info("No data available for this query.")
        return


    # 1) Vehicle-based
    if analysis_option == "Top 10 Vehicles in Drug Related Stops":
        chart_data = df.set_index("vehicle_number")["drug_stop_count"]
        st.bar_chart(chart_data)


    elif analysis_option == "Most Frequently Searched Vehicles":
        chart_data = df.set_index("vehicle_number")["times_searched"]
        st.bar_chart(chart_data)


    # 2) Demographic-based
    elif analysis_option == "Driver Age Group with Highest Arrest Rate":
        # show arrest rate by driver_age
        chart_data = df.set_index("driver_age")["arrest_rate_pct"]
        st.bar_chart(chart_data)


    elif analysis_option == "Gender Distribution by Country":
        # Pie chart of total gender distribution (ignores country split)
        gender_totals = df.groupby("driver_gender")["count"].sum().reset_index()


        fig, ax = plt.subplots()
        ax.pie(
            gender_totals["count"],
            labels=gender_totals["driver_gender"],
            autopct="%1.1f%%",
            startangle=90,
        )
        ax.set_title("Overall Gender Distribution")
        st.pyplot(fig)


    elif analysis_option == "Race x Gender - Highest Search Rate":
        df["race_gender"] = df["driver_race"] + " - " + df["driver_gender"]
        chart_data = df.set_index("race_gender")["search_rate"]
        st.bar_chart(chart_data)


    # 3) Time & duration based
    elif analysis_option == "Time of Day with Most Traffic Stops":
        chart_data = df.set_index("stop_hour")["stops"]
        st.bar_chart(chart_data)


    elif analysis_option == "Average Stop Duration by Violation":
        chart_data = df.set_index("violation")["avg_minutes"]
        st.bar_chart(chart_data)


    elif analysis_option == "Night vs Day Arrest Likelihood":
        # Pie for stops, bar for arrests
        st.write("Stops (Night vs Day)")
        fig, ax = plt.subplots()
        ax.pie(
            df["stops"],
            labels=df["time_period"],
            autopct="%1.1f%%",
            startangle=90,
        )
        ax.set_title("Stops: Night vs Day")
        st.pyplot(fig)


        st.write("Arrests (Night vs Day)")
        chart_data = df.set_index("time_period")["arrests"]
        st.bar_chart(chart_data)


    # 4) Violation-based
    elif analysis_option == "Violations with Highest Search or Arrest":
        chart_data = df.set_index("violation")[["searches", "arrests"]]
        st.bar_chart(chart_data)


    elif analysis_option == "Violations common among Drivers < 25":
        chart_data = df.set_index("violation")["count"]
        st.bar_chart(chart_data)


    elif analysis_option == "Violations with Rare Search or Arrest":
        chart_data = df.set_index("violation")[["stops", "searches", "arrests"]]
        st.bar_chart(chart_data)


    # 5) Location-based
    elif analysis_option == "Countries with Highest Drug-Related Stops":
        chart_data = df.set_index("country_name")[["drug_stops", "total_stops"]]
        st.bar_chart(chart_data)


    elif analysis_option == "Arrest Rate by Country and Violation":
        # aggregate by country for chart
        temp = df.groupby("country_name")["arrests"].sum().reset_index()
        chart_data = temp.set_index("country_name")["arrests"]
        st.bar_chart(chart_data)


    elif analysis_option == "Countries with Most Searches Conducted":
        chart_data = df.set_index("country_name")["search_count"]
        st.bar_chart(chart_data)

    # -----------------------------
    # COMPLEX LEVEL CHARTS
    # -----------------------------

    elif analysis_option == "Yearly Breakdown of Stops and Arrests by Country":
        rate_df = (
            df.groupby(["stop_year", "country_name"])["arrest_rate_pct"]
            .mean()
            .reset_index()
            .pivot(index="stop_year", columns="country_name", values="arrest_rate_pct")
            .fillna(0)
        )

        st.line_chart(rate_df)


    elif analysis_option == "Driver Violation Trends Based on Age and Race":
        chart_data = (
            df.groupby(["violation", "age_group"])["violation_count"]
            .sum()
            .reset_index()
            .pivot(index="violation", columns="age_group", values="violation_count")
            .fillna(0)
            .sort_values(by=list(df["age_group"].unique()), ascending=False)
            .head(10)
        )
        st.bar_chart(chart_data)


    elif analysis_option == "Time Period Analysis of Stops (Year, Month, Hour)":
        hourly = (
            df.groupby("stop_hour")["total_stops"]
            .sum()
        )
        st.line_chart(hourly)

    elif analysis_option == "Violations with High Search and Arrest Rates":
        chart_data = df.set_index("violation")[["search_rate_pct", "arrest_rate_pct"]]
        st.bar_chart(chart_data)

    
    elif analysis_option == "Driver Demographics by Country":
        demo = (
            df.groupby(["country_name", "age_group"])["total_stops"]
            .sum()
            .reset_index()
            .pivot(index="country_name", columns="age_group", values="total_stops")
            .fillna(0)
        )
        st.bar_chart(demo)

    elif analysis_option == "Top 5 Violations with Highest Arrest Rates":
        chart_data = df.set_index("violation")["arrest_rate_pct"]
        st.bar_chart(chart_data)    

    else:
        st.info("No chart defined for this analysis.")



# -------------------------------------------------
# Streamlit App
# -------------------------------------------------
st.set_page_config(page_title="Traffic Stop Monitoring Dashboard", layout="wide")


# -------------------------
# Sidebar Navigation
# -------------------------
st.sidebar.title("Navigation")

menu = st.sidebar.radio(
    "Menu",
    ["Dashboard", "Police Summary"]
)



# -------------------------
# DASHBOARD SECTION
# -------------------------
if menu == "Dashboard":

    st.title("🚦 Traffic Stop Monitoring Dashboard (First 1000 Records)")
    
    # Load only first 1000 rows to keep app fast

    df = pd.read_sql("SELECT * FROM traffic_dat LIMIT 1000", conn)

    st.dataframe(df, use_container_width=True)

    # filters
    # analytics
    # charts


# -------------------------
# POLICE SUMMARY SECTION
# -------------------------
elif menu == "Police Summary":

    st.subheader("📝 Police Stop Summary Generator")

    with st.form("summary_form"):

        vehicle_number = st.text_input("Vehicle Number")

        submit = st.form_submit_button("Generate Summary")


# -------------------------------------------------
# SUMMARY GENERATED FROM DATASET (NOT USER INPUT)
# -------------------------------------------------
    if submit:

    # 1️⃣ Primary lookup using vehicle number
        matched_df = df[df["vehicle_number"] == vehicle_number]

        if matched_df.empty:
            st.warning("⚠️ No police stop found for this vehicle number.")
        else:
        # 2️⃣ Pick first matching record
            record = matched_df.iloc[0]

        # 3️⃣ Format stop time
            try:
                time_str = pd.to_datetime(record["stop_time"]).strftime("%I:%M %p")
            except:
                time_str = str(record["stop_time"])

        # 4️⃣ Convert flags into readable text
            search_text = (
                "No search was conducted"
                if record["search_conducted"] in [0, "FALSE", False]
                else "A search was conducted"
            )

            drug_text = (
                "not drug-related"
                if record["drugs_related_stop"] in [0, "FALSE", False]
                else "drug-related"
            )

            gender_text = (
                "male" if record["driver_gender"] in ["M", "Male"] else
                "female" if record["driver_gender"] in ["F", "Female"] else
                "driver"
            )

        # 5️⃣ Generate summary from DATA
            summary = (
                f"🚗 A {int(record['driver_age'])}-year-old {gender_text} driver "
                f"was stopped for {record['violation']} at {time_str}. "
                f"{search_text}, and the stop resulted in a "
                f"{record['stop_outcome']}. "
                f"The stop lasted {record['stop_duration']} and was {drug_text}."
            )

        # 6️⃣ Display result
            st.success("📄 Police Stop Summary (Generated from Dataset)")
            st.write(summary)

        # Optional: show matched record
            with st.expander("🔍 View Matched Record"):
                st.dataframe(matched_df)

# ----------------------------
# Filters section
# ----------------------------
st.subheader("🔍 Search Filters")


country = st.selectbox(
    "Country",
    ["All"] + sorted(df["country_name"].dropna().unique().tolist())
)


violation = st.selectbox(
    "Violation",
    ["All"] + sorted(df["violation"].dropna().unique().tolist())
)


filtered = df.copy()


if country != "All":
    filtered = filtered[filtered["country_name"] == country]


if violation != "All":
    filtered = filtered[filtered["violation"] == violation]


st.subheader("Filtered Results")
st.dataframe(filtered, use_container_width=True)


st.markdown("---")


# ----------------------------
# SQL Analytics Section
# ----------------------------
st.subheader("📊 Data Insights & Analytics")

#Medium Level Queries and Complex Level Queries
 
#Categorized Select Box

report_categories = {
    "🚗 Vehicle & Searches": [
        "Top 10 Vehicles in Drug Related Stops",
        "Most Frequently Searched Vehicles",
    ],
    "👤 Driver Demographics": [
        "Driver Age Group with Highest Arrest Rate",
        "Gender Distribution by Country",
        "Race x Gender - Highest Search Rate",
    ],
    "⏱ Time-Based Analysis": [
        "Time of Day with Most Traffic Stops",
        "Night vs Day Arrest Likelihood",
    ],
    "⚠ Violations Analysis": [
        "Average Stop Duration by Violation",
        "Violations with Highest Search or Arrest",
        "Violations common among Drivers < 25",
        "Violations with Rare Search or Arrest",
    ],
    "🌍 Country-Level Insights": [
        "Countries with Highest Drug-Related Stops",
        "Arrest Rate by Country and Violation",
        "Countries with Most Searches Conducted",
    ],
    "🧠 Complex Analysis": [
    "Yearly Breakdown of Stops and Arrests by Country",
    "Driver Violation Trends Based on Age and Race",
    "Time Period Analysis of Stops (Year, Month, Hour)",
    "Violations with High Search and Arrest Rates",
    "Driver Demographics by Country",
    "Top 5 Violations with Highest Arrest Rates",
]

}

#Category Selectbox

category = st.selectbox(
    "Select Category",
    list(report_categories.keys())
)

#Question Selectbox

analysis_option = st.selectbox(
    "Select Question",
    report_categories[category]
)

#Query Part 

queries = {
    "Top 10 Vehicles in Drug Related Stops": """
        SELECT vehicle_number, COUNT(*) AS drug_stop_count
        FROM traffic_dat
        WHERE drugs_related_stop = 1
        GROUP BY vehicle_number
        ORDER BY drug_stop_count DESC
        LIMIT 10;
    """,


    "Most Frequently Searched Vehicles": """
        SELECT vehicle_number, COUNT(*) AS times_searched
        FROM traffic_dat
        WHERE search_conducted = 1 
        GROUP BY vehicle_number
        ORDER BY times_searched DESC
        LIMIT 10;
    """,


    "Driver Age Group with Highest Arrest Rate": """
        SELECT driver_age,
               COUNT(*) AS stops,
               SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS arrests,
               ROUND(100.0 *
                     SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) /
                     COUNT(*), 2) AS arrest_rate_pct
        FROM traffic_dat
        WHERE driver_age IS NOT NULL
        GROUP BY driver_age
        ORDER BY arrest_rate_pct DESC
        LIMIT 15;
    """,


    "Gender Distribution by Country": """
        SELECT country_name, driver_gender, COUNT(*) AS count
        FROM traffic_dat
        GROUP BY country_name, driver_gender
        ORDER BY country_name, count DESC;
    """,


    "Race x Gender - Highest Search Rate": """
        SELECT driver_race, driver_gender,
               COUNT(*) AS stops,
               SUM(CASE WHEN search_conducted = 1 THEN 1 ELSE 0 END) AS searches,
               ROUND(100.0 *
                     SUM(CASE WHEN search_conducted = 1 THEN 1 ELSE 0 END) /
                     COUNT(*), 2) AS search_rate
        FROM traffic_dat
        GROUP BY driver_race, driver_gender
        HAVING stops >= 20
        ORDER BY search_rate DESC
        LIMIT 15;
    """,


    "Time of Day with Most Traffic Stops": """
        SELECT CAST(strftime('%H', stop_time) AS INTEGER) AS stop_hour,
               COUNT(*) AS stops
        FROM traffic_dat
        GROUP BY stop_hour
        ORDER BY stop_hour;
    """,


    "Average Stop Duration by Violation": """
        SELECT violation,
               COUNT(*) AS stops,
               AVG(duration_min) AS avg_minutes
        FROM (
            SELECT violation,
                   CASE
                       WHEN stop_duration = '<5 min' THEN 5
                       WHEN stop_duration IN ('6-15 min', '6-15 Min') THEN 10
                       WHEN stop_duration IN ('16-30 min', '16-30 Min') THEN 25
                       WHEN stop_duration IN ('31-60 min', '31-60 Min') THEN 45
                       WHEN stop_duration LIKE '>60%%' THEN 75
                       ELSE NULL
                   END AS duration_min
            FROM traffic_dat
        ) t
        WHERE duration_min IS NOT NULL
        GROUP BY violation
        ORDER BY avg_minutes DESC;
    """,


    "Night vs Day Arrest Likelihood": """
        SELECT
            CASE
                WHEN CAST(strftime('%H', stop_time) AS TIME) BETWEEN 20 AND 23 THEN 'Night'
                WHEN CAST(strftime('%H', stop_time) AS TIME) BETWEEN 0 AND 5 THEN 'Night'
                ELSE 'Day'
            END AS time_period,
            COUNT(*) AS stops,
            SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS arrests
        FROM traffic_dat
        GROUP BY time_period;
    """,


    "Violations with Highest Search or Arrest": """
        SELECT violation,
               COUNT(*) AS stops,
               SUM(CASE WHEN search_conducted = 1 THEN 1 ELSE 0 END) AS searches,
               SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS arrests
        FROM traffic_dat
        GROUP BY violation
        HAVING stops >= 20
        ORDER BY searches DESC, arrests DESC
        LIMIT 15;
    """,


    "Violations common among Drivers < 25": """
        SELECT violation, COUNT(*) AS count
        FROM traffic_dat
        WHERE driver_age < 25
        GROUP BY violation
        ORDER BY count DESC
        LIMIT 15;
    """,


    "Violations with Rare Search or Arrest": """
        SELECT violation,
               COUNT(*) AS stops,
               SUM(CASE WHEN search_conducted = 1 THEN 1 ELSE 0 END) AS searches,
               SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS arrests
        FROM traffic_dat
        GROUP BY violation
        HAVING searches = 0 AND arrests = 0;
    """,


    "Countries with Highest Drug-Related Stops": """
        SELECT country_name,
               COUNT(*) AS total_stops,
               SUM(CASE WHEN drugs_related_stop = 1 THEN 1 ELSE 0 END) AS drug_stops,
               ROUND(100.0 *
                     SUM(CASE WHEN drugs_related_stop = 1 THEN 1 ELSE 0 END) /
                     COUNT(*), 2) AS drug_rate_pct
        FROM traffic_dat
        GROUP BY country_name
        ORDER BY drug_rate_pct DESC;
    """,


    "Arrest Rate by Country and Violation": """
        SELECT country_name, violation,
               COUNT(*) AS stops,
               SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS arrests,
               ROUND(100.0 *
                     SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) /
                     COUNT(*), 2) AS arrest_rate_pct
        FROM traffic_dat
        GROUP BY country_name, violation
        HAVING stops >= 10
        ORDER BY arrest_rate_pct DESC;
    """,


    "Countries with Most Searches Conducted": """
        SELECT country_name, COUNT(*) AS search_count
        FROM traffic_dat
        WHERE search_conducted = 1
        GROUP BY country_name
        ORDER BY search_count DESC;
    """,

"Yearly Breakdown of Stops and Arrests by Country": """
SELECT
     country_name,
     CAST(strftime('%Y', stop_date) AS INTEGER) AS stop_year,
    COUNT(*) AS total_stops,
    SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS total_arrests,
    ROUND(
        100.0 * SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS arrest_rate_pct
FROM traffic_dat
GROUP BY country_name, stop_year
ORDER BY stop_year;
""",


"Driver Violation Trends Based on Age and Race": """
SELECT
    age_group,
    driver_race,
    violation,
    COUNT(*) AS violation_count
FROM (
    SELECT *,
        CASE
            WHEN driver_age < 25 THEN 'Under 25'
            WHEN driver_age BETWEEN 25 AND 40 THEN '25-40'
            WHEN driver_age BETWEEN 41 AND 60 THEN '41-60'
            ELSE '60+'
        END AS age_group
    FROM traffic_dat
) t
GROUP BY age_group, driver_race, violation
HAVING violation_count >= 20
ORDER BY violation_count DESC;
""",

"Time Period Analysis of Stops (Year, Month, Hour)": """
SELECT
    CAST(strftime('%Y', stop_date) AS INTEGER) AS stop_year,
    CAST(strftime('%m', stop_date) AS INTEGER) AS stop_month,
    CAST(strftime('%H', stop_time) AS INTEGER) AS stop_hour,
    COUNT(*) AS total_stops
FROM traffic_dat
GROUP BY stop_year, stop_month, stop_hour
ORDER BY stop_year, stop_month, stop_hour
LIMIT 500;
""",


"Violations with High Search and Arrest Rates": """
SELECT
    violation,
    COUNT(*) AS total_stops,
    SUM(CASE WHEN search_conducted = 1 THEN 1 ELSE 0 END) AS searches,
    SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS arrests,
    ROUND(100.0 * SUM(search_conducted = 1) / COUNT(*), 2) AS search_rate_pct,
    ROUND(100.0 * SUM(is_arrested = 1) / COUNT(*), 2) AS arrest_rate_pct
FROM traffic_dat
GROUP BY violation
HAVING total_stops >= 20
ORDER BY arrest_rate_pct DESC;
""",

"Driver Demographics by Country": """
SELECT
    country_name,
    CASE
        WHEN driver_age < 25 THEN 'Under 25'
        WHEN driver_age BETWEEN 25 AND 40 THEN '25-40'
        WHEN driver_age BETWEEN 41 AND 60 THEN '41-60'
        ELSE '60+'
    END AS age_group,
    driver_gender,
    driver_race,
    COUNT(*) AS total_stops
FROM traffic_dat
GROUP BY country_name, age_group, driver_gender, driver_race
ORDER BY country_name, total_stops DESC;
""",

"Top 5 Violations with Highest Arrest Rates": """
SELECT
    violation,
    COUNT(*) AS total_stops,
    SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS arrests,
    ROUND(
        100.0 * SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS arrest_rate_pct
FROM traffic_dat
GROUP BY violation
HAVING total_stops >= 20
ORDER BY arrest_rate_pct DESC
LIMIT 5;
""",

}


sql = queries[analysis_option]
cursor.execute(sql)
result = cursor.fetchall()
analysis_df = pd.DataFrame(result, columns=[col[0] for col in cursor.description])


st.markdown("### 📄 Query Result")
st.dataframe(analysis_df.head(100), use_container_width=True)


st.markdown("### 📊 Visualization")
render_chart(analysis_option, analysis_df)


# Close DB Connection

cursor.close()
conn.close()
