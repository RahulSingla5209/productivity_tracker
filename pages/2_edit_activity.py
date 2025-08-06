import streamlit as st
import json
import os
import datetime

ACTIVITIES_FILE = "activities.json"

def load_activities():
    if os.path.exists(ACTIVITIES_FILE):
        with open(ACTIVITIES_FILE, "r") as f:
            return json.load(f)
    return []

def save_activities(activities):
    with open(ACTIVITIES_FILE, "w") as f:
        json.dump(activities, f, indent=2)

def main():
    st.header("✏️ Edit or Delete Activities")
    activities = load_activities()
    
    if not activities:
        st.info("No activities to edit. Add some activities first!")
        return

    # Show activities in a table, most recent first
    activities_sorted = list(reversed(activities))
    activity_labels = [
        f"{act['date']} | {act['name']} ({act['category']}) [{act['points']} pts] - {act['user']}"
        for act in activities_sorted
    ]
    selected = st.selectbox("Select an activity to edit or delete:", activity_labels)

    selected_idx = activity_labels.index(selected)
    selected_activity = activities_sorted[selected_idx]

    # Edit form
    with st.form("edit_activity_form"):
        new_name = st.text_input("Activity Name", selected_activity["name"])
        new_category = st.selectbox("Category", [
            "Physical Workout", "Mental Workout", "Creative Exercise", "Others"
        ], index=[
            "Physical Workout", "Mental Workout", "Creative Exercise", "Others"
        ].index(selected_activity["category"]))
        new_points = st.number_input("Points", min_value=1, max_value=100, value=int(selected_activity["points"]))
        new_user = st.text_input("User", selected_activity["user"])
        date_val = datetime.datetime.strptime(selected_activity["date"], "%Y-%m-%d %H:%M")
        new_date = st.date_input("Date", date_val.date())
        new_time = st.time_input("Time", date_val.time())
        
        edit_submitted = st.form_submit_button("Save Changes")
        delete_submitted = st.form_submit_button("Delete Activity")

        if edit_submitted:
            # Update the activity in the list
            updated_activity = {
                "name": new_name,
                "category": new_category,
                "points": int(new_points),
                "user": new_user,
                "date": datetime.datetime.combine(new_date, new_time).strftime("%Y-%m-%d %H:%M")
            }
            # Find original index in the file
            orig_idx = len(activities) - 1 - selected_idx
            activities[orig_idx] = updated_activity
            save_activities(activities)
            st.success("Activity updated! Refresh or re-select to see changes.")

        if delete_submitted:
            orig_idx = len(activities) - 1 - selected_idx
            activities.pop(orig_idx)
            save_activities(activities)
            st.success("Activity deleted! Refresh to update the list.")

if __name__ == "__main__":
    main()
