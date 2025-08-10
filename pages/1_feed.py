# pages/1_Feed.py
import streamlit as st
import pandas as pd
import altair as alt
from common import (
    get_supabase, require_user, user_chip,
    get_browser_timezone, to_local_series, go_to_add,
    pop_flash_success
)

st.header("📋 Activity Feed")
user = require_user()
user_chip()
pop_flash_success()  # shows “Added …” once

sb = get_supabase()
resp = (
    sb.table("activities")
    .select("*")
    .eq("user_id", user["user_id"])
    .order("date", desc=True)
    .execute()
)
data = resp.data or []
if not data:
    st.info("No activities to show yet. Add some activities!")
    if st.button("➕ Add Activity"):
        go_to_add()
    st.stop()

# --- Build base dataframe ---
df = pd.DataFrame(data)

tz = get_browser_timezone("tz-feed")
df["date_local"] = to_local_series(df.get("date"), tz)

# Drop rows without valid timestamps
df = df[df["date_local"].notna()].copy()

# Safe types
df["duration_minutes"] = pd.to_numeric(df.get("duration_minutes"), errors="coerce").fillna(0).astype(int)
df["category"] = df.get("category").astype(str).fillna("Uncategorized")

# Day column for grouping
df["day"] = df["date_local"].dt.date

st.markdown("---")
if st.button("➕ Add Activity"):
    go_to_add()

############### Chart (Altair) ###############
plot_df = df[df["duration_minutes"] > 0].copy()
if plot_df.empty:
    st.info("No minutes to chart yet. Add some activities!")
else:
    grouped = (
        plot_df.groupby(["day", "category"], as_index=False)["duration_minutes"]
        .sum()
        .rename(columns={"day": "date", "duration_minutes": "minutes"})
    )

    grouped["date"] = pd.to_datetime(grouped["date"], errors="coerce")
    grouped = grouped[grouped["date"].notna()].copy()
    grouped["category"] = grouped["category"].astype(str)
    grouped["minutes"] = pd.to_numeric(grouped["minutes"], errors="coerce").fillna(0)

    st.subheader("Minutes per Day (by Category)")

    if grouped.empty:
        st.info("No minutes to chart yet. Add some activities!")
    else:
        legend_sel = alt.selection_point(fields=["category"], bind="legend")

        line = (
            alt.Chart(grouped)
            .mark_line(point=False)
            .encode(
                x=alt.X("date:T", title="Date"),
                y=alt.Y("minutes:Q", title="Minutes"),
                color=alt.Color("category:N", title="Category"),
                opacity=alt.condition(legend_sel, alt.value(1.0), alt.value(0.25)),
                tooltip=[
                    alt.Tooltip("date:T", title="Date"),
                    alt.Tooltip("category:N", title="Category"),
                    alt.Tooltip("minutes:Q", title="Minutes"),
                ],
            )
            .add_params(legend_sel)
        )

        points = (
            alt.Chart(grouped)
            .mark_circle(size=50)
            .encode(
                x="date:T",
                y="minutes:Q",
                color="category:N",
                opacity=alt.condition(legend_sel, alt.value(1.0), alt.value(0.25)),
                tooltip=[
                    alt.Tooltip("date:T", title="Date"),
                    alt.Tooltip("category:N", title="Category"),
                    alt.Tooltip("minutes:Q", title="Minutes"),
                ],
            )
            .add_params(legend_sel)
        )

        chart = (line + points).properties(height=320).interactive()
        st.altair_chart(chart, use_container_width=True)

############# Images #####################
if st.button("📷 Load Feed of Images"):
    st.subheader("Activity Image Gallery")
    images_df = df[
        (~df["image_url"].isna()) & (df["image_url"].astype(str).str.len() > 0)
    ]
    if len(images_df) == 0:
        st.info("No images uploaded. Add some images of activities!")
    else:
        for _, row in images_df.iterrows():
            when = (
                row["date_local"].strftime("%Y-%m-%d %H:%M")
                if pd.notnull(row["date_local"])
                else ""
            )
            mins = int(row.get("duration_minutes", 0) or 0)
            st.image(
                row["image_url"],
                caption=f"{row['name']} ({row['category']}) • {row['user']} • {when} • {mins} min",
                width=400,
            )
    st.markdown("---")
