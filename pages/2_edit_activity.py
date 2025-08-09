import streamlit as st
import pandas as pd
import datetime
import re
import uuid
from common import get_supabase, get_browser_timezone, to_local_series, back_to_feed

st.header("✏️ Edit or Delete Activities")

supabase = get_supabase()
BUCKET = "activity-images"

def public_url(filename: str) -> str:
    return supabase.storage.from_(BUCKET).get_public_url(filename)

def filename_from_url(url: str | None) -> str | None:
    if not url: return None
    url = url.split("?")[0]
    m = re.search(r"/activity-images/([^/]+)$", url)
    return m.group(1) if m else None

# Load
resp = supabase.table("activities").select("*").order("date", desc=True).execute()
df = pd.DataFrame(resp.data or [])
if df.empty:
    st.info("No activities to edit. Add some activities first!")
    if st.button("← Back to Feed"):
        back_to_feed()
    st.stop()

# Localized times for display
tz = get_browser_timezone("tz-edit")
df["date_local"] = to_local_series(df["date"], tz)
df["duration_minutes"] = pd.to_numeric(df.get("duration_minutes"), errors="coerce").fillna(0).astype(int)

# Optional filter by user
users = ["All Users"] + sorted(df["user"].dropna().unique().tolist())
sel_user = st.selectbox("Filter by user (optional)", users, index=0)
dfv = df if sel_user == "All Users" else df[df["user"] == sel_user]

def label_row(r):
    when = r["date_local"].strftime("%Y-%m-%d %H:%M") if pd.notnull(r["date_local"]) else "?"
    return f"{when} | {r['name']} ({r['category']}) [{r['duration_minutes']} min] — {r['user']}"

labels = [label_row(r) for _, r in dfv.iterrows()]
choice = st.selectbox("Pick an activity to edit/delete:", labels)
row = dfv.iloc[labels.index(choice)]

act_id = row["id"]
old_img = row.get("image_url", "")

default_dt = row["date_local"] if pd.notnull(row["date_local"]) else datetime.datetime.now()
default_date = default_dt.date()
default_time = default_dt.time()

with st.form("edit_form"):
    new_name = st.text_input("Activity Name", value=row.get("name", ""))
    new_cat = st.selectbox(
        "Category",
        ["Physical Workout", "Mental Workout", "Creative Exercise", "Others"],
        index=["Physical Workout", "Mental Workout", "Creative Exercise", "Others"].index(row.get("category", "Others"))
        if row.get("category", "Others") in ["Physical Workout", "Mental Workout", "Creative Exercise", "Others"] else 3
    )
    new_mins = st.number_input("Duration (minutes)", min_value=1, max_value=1440, value=int(row.get("duration_minutes", 30) or 30))
    new_user = st.text_input("User", value=row.get("user", "Anonymous"))
    new_date = st.date_input("Date", value=default_date)
    new_time = st.time_input("Time", value=default_time)

    st.caption("Replace image (optional)")
    new_image = st.file_uploader("Upload new image", type=["jpg", "jpeg", "png"], accept_multiple_files=False)

    c1, c2 = st.columns(2)
    save = c1.form_submit_button("💾 Save Changes")
    delete = c2.form_submit_button("🗑️ Delete Activity")

if save:
    naive_dt = datetime.datetime.combine(new_date, new_time)
    dt_local = naive_dt.replace(tzinfo=tz) if tz else naive_dt

    updates = {
        "name": new_name.strip() or row.get("name", ""),
        "category": new_cat,
        "duration_minutes": int(new_mins),
        "user": new_user.strip() or "Anonymous",
        "date": dt_local.isoformat(),
    }

    if new_image is not None:
        ext = new_image.name.split(".")[-1].lower()
        new_filename = f"{uuid.uuid4()}.{ext}"
        supabase.storage.from_(BUCKET).upload(new_filename, new_image.getvalue())
        updates["image_url"] = public_url(new_filename)
        old_file = filename_from_url(old_img or "")
        if old_file:
            try:
                supabase.storage.from_(BUCKET).remove([old_file])
            except Exception:
                pass

    supabase.table("activities").update(updates).eq("id", act_id).execute()
    st.success("Activity updated.")
    st.rerun()

if delete:
    supabase.table("activities").delete().eq("id", act_id).execute()
    old_file = filename_from_url(old_img or "")
    if old_file:
        try:
            supabase.storage.from_(BUCKET).remove([old_file])
        except Exception:
            pass
    st.success("Activity deleted.")
    st.rerun()

st.markdown("---")
if st.button("← Back to Feed"):
    back_to_feed()
