import streamlit as st
from common import (
    get_supabase, require_user, user_chip,
    flash_success
)
import datetime as dt

st.header("➕ Add Activity")
user = require_user()
user_chip()

sb = get_supabase()

activity = st.text_input("Activity Name")
category = st.selectbox("Category", ["Creative Exercise", "Mental Workout", "Physical Workout", "Other"])
duration = st.number_input("Duration (minutes)", min_value=0, max_value=1440)
date_input = st.date_input("Date", dt.date.today())
image_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if st.button("Save Activity"):
    with st.spinner("Saving..."):
        try:
            activity_date: dt.date = date_input
            date_str = activity_date.isoformat()           # 'YYYY-MM-DD'
            date_slug = activity_date.strftime("%Y%m%d")   # for filename

            img_url = None
            if image_file:
                filename = f"{user['user_id']}_{date_slug}.png"
                img_bytes = image_file.read()
                sb.storage.from_("activity-images").upload(filename, image_file.getvalue())
                img_url = sb.storage.from_("activity_images").get_public_url(filename) or ""

            # Insert into DB (DATE column friendly)
            sb.table("activities").insert({
                "user_id": user["user_id"],
                "user": user.get("display_name") or user["user_id"],
                "name": activity.strip(),
                "category": category,
                "duration_minutes": int(duration),
                "date": date_str,          # <-- date only
                "image_url": img_url
            }).execute()

            flash_success(f"Added: {activity} • {duration} min • [{category}] on {activity_date:%Y-%m-%d}")
            # st.success(f"Added: {activity} • {duration} min • [{category}] on {activity_date:%Y-%m-%d}")

        except Exception as e:
            st.error(f"❌ Could not save activity: {e}")
