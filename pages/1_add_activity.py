import streamlit as st
import json
import datetime
import os

CATEGORIES = [
    "Physical Workout",
    "Mental Workout",
    "Creative Exercise",
    "Others"
]

def load_activities():
    if os.path.exists("activities.json"):
        with open("activities.json", "r") as f:
            return json.load(f)
    return []

def save_activity(activity):
    activities = load_activities()
    activities.append(activity)
    with open("activities.json", "w") as f:
        json.dump(activities, f, indent=2)

st.header("➕ Add Your Offline Activity")

with st.form("add_activity_form"):
    user = st.text_input("Your Name (for the feed)", value="You")
    activity = st.text_input("Describe your activity (e.g., Morning Jog, Sudoku, Painting, Gardening, etc.)")
    category = st.selectbox("Select Activity Category", CATEGORIES)
    points = st.number_input("Points for this activity", min_value=1, max_value=100, value=10)
    date_input = st.date_input("Date of Activity", value=datetime.date.today(), max_value=datetime.date.today())
    time_input = st.time_input("Time of Activity", value=datetime.datetime.now().time())
    submitted = st.form_submit_button("Add Activity")

    if submitted:
        if not activity.strip():
            st.warning("Please enter an activity name.")
        else:
            # Combine date and time for a datetime string
            date_time = datetime.datetime.combine(date_input, time_input).strftime("%Y-%m-%d %H:%M")
            act = {
                "user": user if user.strip() else "Anonymous",
                "name": activity,
                "category": category,
                "points": int(points),
                "date": date_time
            }
            save_activity(act)
            st.success(f"Added activity: {activity} (+{points} pts) [{category}] on {date_time}")
