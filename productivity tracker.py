import streamlit as st
from supabase import create_client, Client
import pandas as pd

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.header("📋 Activity Feed (You & Others)")

# Query activities from Supabase
response = supabase.table("activities").select("*").execute()
activities = response.data

if not activities:
    st.info("No activities to show yet. Add some activities!")
else:
    df = pd.DataFrame(activities)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["points"] = pd.to_numeric(df["points"], errors="coerce").fillna(0).astype(int)
    df["day"] = df["date"].dt.date

    # User filter
    st.subheader("User Filter")
    users = ["All Users"] + sorted(df["user"].dropna().unique().tolist())
    selected_user = st.selectbox("Select user for plots", users, index=0)
    if selected_user != "All Users":
        df = df[df["user"] == selected_user]


    # (Rest of plotting code as before)
    grouped = df.groupby(["day", "category"])["points"].sum().reset_index()
    pivot = grouped.pivot(index="day", columns="category", values="points").fillna(0)
    pivot = pivot.sort_index()
    st.subheader("Points per Day (by Category)")
    st.line_chart(pivot)
    
    # Show images if button clicked
    if st.button("📷 Load Feed of Images"):
        st.subheader("Activity Image Gallery")
        images_df = df[(~df["image_url"].isna()) & (df["image_url"].str.len() > 0)]
        for _, row in images_df.iterrows():
            st.image(row["image_url"], caption=f"{row['name']} ({row['category']}) by {row['user']} on {row['date'].strftime('%Y-%m-%d %H:%M')}", width=400)
        st.markdown("---")
