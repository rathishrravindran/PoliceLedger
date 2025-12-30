# 🚦 Police Ledger – Traffic Stop Monitoring Dashboard

A Streamlit-based dashboard for analyzing police traffic stop data using Python and SQL.

---

## 📌 Problem Statement
Police check posts require a centralized system to log, track, and analyze vehicle movements. 
Manual logging and inefficient databases slow down decision-making.

This project solves that problem by:
- Cleaning raw traffic stop data
- Storing it in a database
- Running SQL-based analytics
- Visualizing insights using Streamlit

---

## 🔧 Tech Stack
- Python 
- Pandas - data cleaning & processing
- SQLite - - data cleaning & processing
- Streamlit - interactive dashboard
- Matplotlib - data visualization 

---

## 📂 Project Structure

Police_Ledger/
│
├── Police_Ledger.py # Main Streamlit app
├── traffic_stops.xlsx # Raw dataset
├── cleaned_traffic_stops.csv# Auto-generated
├── traffic.db # SQLite DB (auto-generated)
├── requirements.txt
└── README.md


## ▶️ How to Run the Project

### 1️⃣ Install Python requirements from the associated file

pip install -r requirements.txt


## Run the Streamlit app

streamlit run Police_Ledger_Single.py

⚙️ How the Project Works

Loads raw Excel traffic stop data
Cleans and preprocesses the dataset
Stores cleaned data in SQLite (runs only once)
Executes SQL queries based on user selection
Displays tables, filters, and charts interactively
Allows users to filter data by country and violation
Generates structured insights and summaries

📊 Dashboard Features

Data cleaning & preprocessing
SQLite database initialization (automatic)
SQL analytics (medium & complex queries)
Interactive filters & charts
Analyze:
 - Arrest rates
 - Search frequency
 - Violations
 - Time-based patterns
Time-based and demographic analysis


🧠 Sample Insights

Top vehicles in drug-related stops
Arrest rate by age group and country
Peak traffic stop hours
Violations with high arrest probability

Police Stop Summary Generator

📌 What it does

This feature accepts structured police stop details and generates a clear, human-readable summary describing what happened during the stop.

🔹 Inputs
 - Stop time
 - Driver age
 - Driver gender
 - Driver race
 - Violation
 - Search conducted
 - Search type
 - Stop outcome
 - Stop duration
 - Drug-related stop indicator

🔹 Output (Auto-Generated Summary)

Example:

🚗 A 27-year-old male driver was stopped for Speeding at 2:30 PM.
No search was conducted, and he received a citation.
The stop lasted 6–15 minutes and was not drug-related.


📌 Notes

SQLite is used for easy setup (no password required).

Database and cleaned files are auto-created on first run.

Streamlit reruns are handled safely.
