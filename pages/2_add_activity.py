import streamlit as st
from common import (
    get_supabase, require_user, user_chip, get_browser_timezone,
    flash_success, go_to_feed
)
import datetime as dt
from PIL import Image
import io

st.header("➕ Add Activity")
user = require_user()
user_chip()

sb = get_supabase()

activity = st.text_input("Activity Name")
category = st.selectbox("Category", ["Creative Exercise", "Mental Workout", "Physical Workout", "Other"])
duration = st.number_input("Duration (minutes)", min_value=0, max_value=1440)
date_input = st.date_input("Date", dt.date.today())
time_input = st.time_input("Time", dt.datetime.now().time())
image_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if st.button("Save Activity"):
    with st.spinner("Saving..."):
        try:
            tz = get_browser_timezone("tz-add")
            activity_datetime = dt.datetime.combine(date_input, time_input)
            activity_datetime = activity_datetime.astimezone(tz)

            img_url = None
            if image_file:
                # Create a filename in your Supabase bucket
                filename = f"{user['user_id']}_{activity_datetime}.png"
                img_bytes = image_file.read()

                # Upload to Supabase storage
                sb.storage.from_("activity_images").upload(filename, img_bytes)

                # Get the public URL
                img_url = sb.storage.from_("activity_images").get_public_url(filename)

            # Insert into DB
            sb.table("activities").insert({
                "user_id": user["user_id"],
                "user": user["display_name"],
                "name": activity.strip(),
                "category": category,
                "duration_minutes": int(duration),
                "date": activity_datetime,
                "image_url": img_url
            }).execute()

            flash_success(
                f"Added: {activity} • {duration} min • [{category}] on {activity_datetime:%Y-%m-%d %H:%M %Z}"
            )
            st.success(f"Added: {activity} • {duration} min • [{category}] on {activity_datetime:%Y-%m-%d %H:%M %Z}")

        except Exception as e:
            st.error(f"❌ Could not save activity: {e}")
