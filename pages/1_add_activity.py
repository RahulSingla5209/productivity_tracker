import streamlit as st
import datetime
import uuid
from pathlib import Path
from common import get_supabase, get_browser_timezone, back_to_feed

st.markdown(Path("styles.css").read_text(), unsafe_allow_html=True)

st.header("➕ Add Your Offline Activity")

supabase = get_supabase()
CATEGORIES = ["Physical Workout", "Mental Workout", "Creative Exercise", "Others"]

tz = get_browser_timezone("tz-add")
now_local = datetime.datetime.now(tz) if tz else datetime.datetime.now()

with st.form("add_activity_form"):
    user = st.text_input("Your Name (for the feed)", value="You")
    activity = st.text_input("Describe your activity (e.g., Jog, Sudoku, Painting)")
    category = st.selectbox("Select Activity Category", CATEGORIES)
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=1440, value=30)

    date_input = st.date_input("Date of Activity", value=now_local.date())
    time_input = st.time_input("Time of Activity", value=now_local.time())

    image_file = st.file_uploader("Attach a photo (optional)", type=["jpg", "jpeg", "png"])

    submitted = st.form_submit_button("Add Activity")

    img_url = ""
    if submitted:
        if not activity.strip():
            st.warning("Please enter an activity name.")
        else:
            if image_file:
                ext = image_file.name.split(".")[-1]
                img_filename = f"{uuid.uuid4()}.{ext}"
                supabase.storage.from_("activity-images").upload(img_filename, image_file.getvalue())
                img_url = supabase.storage.from_("activity-images").get_public_url(img_filename) or ""

            naive_dt = datetime.datetime.combine(date_input, time_input)
            dt = naive_dt.replace(tzinfo=tz) if tz else naive_dt

            supabase.table("activities").insert({
                "user": (user or "").strip() or "Anonymous",
                "name": activity.strip(),
                "category": category,
                "duration_minutes": int(duration),
                "date": dt.isoformat(),
                "image_url": img_url,
            }).execute()

            st.success(f"Added: {activity} • {duration} min • [{category}] on {dt:%Y-%m-%d %H:%M %Z}")

if st.button("← Back to Feed"):
    back_to_feed()
