import streamlit as st
import json
import os
import pandas as pd

def load_activities():
    if os.path.exists("activities.json"):
        with open("activities.json", "r") as f:
            return json.load(f)
    return []

st.header("📋 Activity Feed (You & Others)")

activities = load_activities()

if not activities:
    st.info("No activities to show yet. Add some activities!")
else:
    df = pd.DataFrame(activities)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["points"] = pd.to_numeric(df["points"], errors="coerce").fillna(0).astype(int)
    df["day"] = df["date"].dt.date  # just the date part

    # --- USER FILTER ---
    st.subheader("User Filter")
    users = ["All Users"] + sorted(df["user"].dropna().unique().tolist())
    selected_user = st.selectbox("Select user for plots", users, index=0)
    if selected_user != "All Users":
        df = df[df["user"] == selected_user]

    # Aggregate: sum points per day, per category
    grouped = df.groupby(["day", "category"])["points"].sum().reset_index()

    # Pivot for line_chart: rows=day, cols=category, values=points
    pivot = grouped.pivot(index="day", columns="category", values="points").fillna(0)
    pivot = pivot.sort_index()

    st.subheader("Points per Day (by Category)")
    st.line_chart(pivot)  # Each category is a separate line
