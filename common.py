# common.py
import streamlit as st
from supabase import create_client, Client
from zoneinfo import ZoneInfo
import pandas as pd
import bcrypt
from pathlib import Path

USERS_TABLE = "users"
ACT_TABLE = "activities"

# Seven built-in avatars (filenames under static/avatars)
AVATAR_IDS = ["a1.png", "a2.png", "a3.png", "a4.png", "a5.png", "a6.png", "a7.png"]

APP_ROOT = Path(__file__).parent
AVATAR_DIR = APP_ROOT / "static" / "avatars"

@st.cache_resource
def get_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# --------- simple auth (app-level) ----------
def _hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def _check_password(pw: str, pw_hash: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode("utf-8"), pw_hash.encode("utf-8"))
    except Exception:
        return False

def current_user():
    return st.session_state.get("current_user")

def set_current_user(user_dict):
    st.session_state["current_user"] = user_dict

def sign_out():
    if "current_user" in st.session_state:
        del st.session_state["current_user"]
    st.rerun()

def sign_up(user_id: str, password: str, display_name: str, avatar_id: str | None) -> tuple[bool, str]:
    sb = get_supabase()
    if not user_id or not password or not display_name:
        return False, "Please fill all fields."

    # unique id
    exists = sb.table(USERS_TABLE).select("user_id").eq("user_id", user_id).execute().data
    if exists:
        return False, "User ID is already taken. Choose another."

    pw_hash = _hash_password(password)
    sb.table(USERS_TABLE).insert({
        "user_id": user_id,
        "password_hash": pw_hash,
        "display_name": display_name,
        "avatar_id": avatar_id or None
    }).execute()

    set_current_user({
        "user_id": user_id,
        "display_name": display_name,
        "avatar_id": avatar_id or None
    })
    return True, "Account created."

def sign_in(user_id: str, password: str) -> tuple[bool, str]:
    sb = get_supabase()
    rows = sb.table(USERS_TABLE).select("*").eq("user_id", user_id).limit(1).execute().data
    if not rows:
        return False, "No such user id."
    u = rows[0]
    if not _check_password(password, u["password_hash"]):
        return False, "Incorrect password."
    set_current_user({
        "user_id": u["user_id"],
        "display_name": u["display_name"],
        "avatar_id": u.get("avatar_id")
    })
    return True, "Signed in."

def encode_password(pw: str) -> str:
    return _hash_password(pw)

def require_user():
    u = current_user()
    if not u:
        st.info("Please sign in or sign up on Home.")
        st.stop()
    return u

# --------- avatars ----------
def avatar_path(avatar_id: str | None):
    if not avatar_id:
        return None
    return str(AVATAR_DIR / avatar_id)

def avatar_picker(key: str = "avatar_choice", default: str | None = None) -> str | None:
    # Show 7 avatars as a grid; return selected filename
    st.caption("Choose an avatar")
    cols = st.columns(len(AVATAR_IDS))
    # default to first if invalid
    sel = default if default in AVATAR_IDS else AVATAR_IDS[0]
    idx_default = AVATAR_IDS.index(sel)
    # radio with labels (hidden) + show images
    choice = st.radio(" ", AVATAR_IDS, index=idx_default, key=key, label_visibility="collapsed", horizontal=True)
    for i, c in enumerate(cols):
        with c:
            st.image(str(AVATAR_DIR / AVATAR_IDS[i]), width=48)
    return choice

def user_chip(top_right: bool = True):
    u = current_user()
    if not u:
        return
    col1, col2 = st.columns([9, 1]) if top_right else st.columns([1, 9])
    with (col2 if top_right else col1):
        ap = avatar_path(u.get("avatar_id"))
        if ap:
            st.image(ap, width=32)
        st.caption(u.get("display_name", u.get("user_id", "")))

# --------- timezone ----------
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

# --------- nav helpers ----------
def go_to_feed():
    st.switch_page("pages/1_Feed.py")

def go_to_add():
    st.switch_page("pages/2_Add_Activity.py")

def go_to_profile():
    st.switch_page("pages/4_Profile.py")


# ---- flash helpers ----
def flash_success(msg: str): st.session_state["flash_success"] = msg
def pop_flash_success():
    msg = st.session_state.pop("flash_success", None)
    if msg: st.success(msg)