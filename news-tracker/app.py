import os
import streamlit as st

def load_reports(run_dir="data/runs"):
    reports = []
    if not os.path.exists(run_dir):
        return reports
    for root, dirs, files in os.walk(run_dir):
        for file in files:
            if file.endswith("report.md"):
                reports.append(os.path.join(root, file))
    return sorted(reports, reverse=True)

st.set_page_config(page_title="Global News Tracker", layout="wide")
st.title("🌍 Global News Topic Tracker")

reports = load_reports()

if not reports:
    st.warning("No reports found. Please run `python tracker.py` first.")
else:
    selected_report = st.selectbox("Select a report", reports)
    with open(selected_report, "r", encoding="utf-8") as f:
        content = f.read()
    st.markdown(content)
