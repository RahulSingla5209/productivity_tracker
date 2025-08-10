import streamlit as st
import pandas as pd
from common import get_supabase, get_browser_timezone, to_local_series

st.header("📋 Activity Feed")

supabase = get_supabase()

# Fetch activities
resp = supabase.table("activities").select("*").execute()
data = resp.data or []
df = pd.DataFrame(data)

# Timezone-aware display
tz = get_browser_timezone("tz-feed")
df["date_local"] = to_local_series(df["date"], tz)
df["day"] = df["date_local"].dt.date
df["duration_minutes"] = pd.to_numeric(df.get("duration_minutes"), errors="coerce").fillna(0).astype(int)

# Sidebar: navigation and filter
with st.sidebar:
    if st.button("➕ Add Activity"):
        st.switch_page("pages/1_add_activity.py")
    if st.button("✏️ Edit Activity"):
        st.switch_page("pages/2_edit_activity.py")

    st.markdown("---")
    st.subheader("User Filter")
    users = ["All Users"] + sorted(df["user"].dropna().unique().tolist())
    selected_user = st.selectbox("Select user for plots", users, index=0)

if df.empty:
    st.info("No activities to show yet. Add some activities!")
    st.stop()

if selected_user != "All Users":
    df = df[df["user"] == selected_user]

# Minutes per day by category
grouped = df.groupby(["day", "category"])["duration_minutes"].sum().reset_index()
pivot = grouped.pivot(index="day", columns="category", values="duration_minutes").fillna(0).sort_index()
st.subheader("Minutes per Day (by Category)")
st.line_chart(pivot)

# Image gallery
if st.button("📷 Load Feed of Images"):
    st.subheader("Activity Image Gallery")
    images_df = df[(~df["image_url"].isna()) & (df["image_url"].astype(str).str.len() > 0)]
    for _, row in images_df.iterrows():
        when = row["date_local"].strftime("%Y-%m-%d %H:%M") if pd.notnull(row["date_local"]) else ""
        mins = int(row.get("duration_minutes", 0) or 0)
        st.image(
            row["image_url"],
            caption=f"{row['name']} ({row['category']}) • {row['user']} • {when} • {mins} min",
            width=400,
        )
    st.markdown("---")
