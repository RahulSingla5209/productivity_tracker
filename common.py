# common.py (no auth)
import streamlit as st
from supabase import create_client, Client
from zoneinfo import ZoneInfo
import pandas as pd

# ---------- Supabase ----------
@st.cache_resource
def get_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# ---------- Timezone helpers ----------
def get_browser_timezone(key: str) -> ZoneInfo | None:
    try:
        from streamlit_js_eval import streamlit_js_eval
        tzname = streamlit_js_eval(
            js_expressions="Intl.DateTimeFormat().resolvedOptions().timeZone",
            key=key,
            want_output=True,
        )
        return ZoneInfo(tzname) if tzname else None
    except Exception:
        return None

def to_local_series(ts_series, tz: ZoneInfo | None):
    s = pd.to_datetime(ts_series, errors="coerce", utc=True)
    return s.dt.tz_convert(tz) if tz else s

# ---------- Nav ----------
def go_to_add_activity():
    st.switch_page("pages/1_add_activity.py")

def back_to_feed():
    st.switch_page("productivity tracker.py")
