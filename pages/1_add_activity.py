import streamlit as st
from supabase import create_client, Client
import datetime
import uuid
import os

# Set your Supabase URL and anon key here (keep anon key safe)
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

CATEGORIES = [
    "Physical Workout",
    "Mental Workout",
    "Creative Exercise",
    "Others"
]

st.header("➕ Add Your Offline Activity")

with st.form("add_activity_form"):
    user = st.text_input("Your Name (for the feed)", value="You")
    activity = st.text_input("Describe your activity (e.g., Jog, Sudoku, Painting)")
    category = st.selectbox("Select Activity Category", CATEGORIES)
    points = st.number_input("Points for this activity", min_value=1, max_value=100, value=10)
    date_input = st.date_input("Date of Activity", value=datetime.date.today(), max_value=datetime.date.today())
    time_input = st.time_input("Time of Activity", value=datetime.datetime.now().time())
    image_file = st.file_uploader("Attach a photo (optional)", type=["jpg", "jpeg", "png"])

    submitted = st.form_submit_button("Add Activity")

    img_url = None
    if submitted:
        if not activity.strip():
            st.warning("Please enter an activity name.")
        else:
            # 1. Upload image if provided
            if image_file:
                ext = image_file.name.split('.')[-1]
                img_filename = f"{uuid.uuid4()}.{ext}"
                # Use getvalue() to pass bytes, NOT the UploadedFile object
                res = supabase.storage.from_('activity-images').upload(img_filename, image_file.getvalue())
                img_url = supabase.storage.from_('activity-images').get_public_url(img_filename)

            # 2. Combine date and time
            date_time = datetime.datetime.combine(date_input, time_input)
            # 3. Insert into Supabase
            new_activity = {
                "user": user if user.strip() else "Anonymous",
                "name": activity,
                "category": category,
                "points": int(points),
                "date": date_time.isoformat(),
                "image_url": img_url if img_url else ""
            }
            data, count = supabase.table("activities").insert(new_activity).execute()
            st.success(f"Added activity: {activity} (+{points} pts) [{category}] on {date_time}")
