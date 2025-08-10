# common.py
import streamlit as st
from supabase import create_client, Client
from zoneinfo import ZoneInfo
import pandas as pd
from pathlib import Path

USERS_TABLE = "users"
ACT_TABLE = "activities"

# Seven built-in avatars (filenames under static/avatars)
AVATAR_IDS = ["a1.png", "a2.png", "a3.png", "a4.png", "a5.png", "a6.png", "a7.png"]

APP_ROOT = Path(__file__).parent
AVATAR_DIR = APP_ROOT / "static" / "avatars"

# ---------------- Supabase client ----------------
@st.cache_resource
def get_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# ---------------- Auth/session helpers ----------------
def _sync_or_create_user_row(sb: Client, auth_user) -> dict:
    """
    Ensure there's a row in public.users linked to this auth user.
    Returns the users row shaped like your app expects.
    """
    # 1) Try by auth_id
    resp = sb.table(USERS_TABLE).select("*").eq("auth_id", auth_user.id).limit(1).execute()
    row = (resp.data or [None])[0]
    if row:
        return row

    # 2) Try by email
    email = auth_user.email
    if email:
        resp = sb.table(USERS_TABLE).select("*").eq("email", email).limit(1).execute()
        row = (resp.data or [None])[0]
        if row:
            # attach auth_id and return
            sb.table(USERS_TABLE).update({"auth_id": auth_user.id}).eq("user_id", row["user_id"]).execute()
            row["auth_id"] = auth_user.id
            return row

    # 3) Create a new row (username from email local-part; add suffix if taken)
    #    If there's no email (rare), fallback to 'user' base name.
    base = (email.split("@")[0] if email and "@" in email else "user").strip() or "user"
    username = base
    suffix = 1
    while True:
        exists = sb.table(USERS_TABLE).select("user_id").eq("user_id", username).limit(1).execute().data
        if not exists:
            break
        suffix += 1
        username = f"{base}{suffix}"

    new_row = {
        "user_id": username,
        "display_name": username,
        "avatar_id": "a1.png",
        "email": email,
        "auth_id": auth_user.id,
    }
    sb.table(USERS_TABLE).insert(new_row).execute()
    return new_row

def current_user_row():
    """
    Returns your app's user row (from public.users) for the signed-in auth user,
    or None if not signed in.
    """
    sb = get_supabase()
    session = sb.auth.get_session()
    if not session or not session.user:
        return None
    return _sync_or_create_user_row(sb, session.user)

def require_user():
    u = current_user_row()
    if not u:
        st.error("Please sign in to continue.")
        st.stop()
    return u

def sign_out():
    sb = get_supabase()
    try:
        sb.auth.sign_out()
    finally:
        st.rerun()

def user_chip(top_right: bool = True):
    u = current_user_row()
    if not u:
        return
    col1, col2 = st.columns([9, 1]) if top_right else st.columns([1, 9])
    with (col2 if top_right else col1):
        ap = avatar_path(u.get("avatar_id"))
        if ap:
            st.image(ap, width=32)
        st.caption(u.get("display_name") or u.get("user_id") or u.get("email") or "")

# ---------------- Avatar helpers ----------------
def avatar_path(avatar_id: str | None):
    if not avatar_id:
        return None
    return str(AVATAR_DIR / avatar_id)

def avatar_picker(key: str = "avatar_choice", default: str | None = None) -> str | None:
    st.caption("Choose an avatar")
    cols = st.columns(len(AVATAR_IDS))
    sel = default if default in AVATAR_IDS else AVATAR_IDS[0]
    idx_default = AVATAR_IDS.index(sel)
    choice = st.radio(" ", AVATAR_IDS, index=idx_default, key=key,
                      label_visibility="collapsed", horizontal=True)
    for i, c in enumerate(cols):
        with c:
            st.image(str(AVATAR_DIR / AVATAR_IDS[i]), width=48)
    return choice

# ---------------- Timezone / dates ----------------
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

# ---------------- Navigation ----------------
def go_to_feed():
    st.switch_page("pages/1_Feed.py")

def go_to_add():
    st.switch_page("pages/2_Add_Activity.py")

def go_to_profile():
    st.switch_page("pages/4_Profile.py")

# ---------------- Flash messages ----------------
def flash_success(msg: str):
    st.session_state["flash_success"] = msg

def pop_flash_success():
    msg = st.session_state.pop("flash_success", None)
    if msg:
        st.success(msg)
