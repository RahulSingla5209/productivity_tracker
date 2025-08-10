# pages/4_Profile.py
import streamlit as st
import pandas as pd
from common import (
    get_supabase, require_user, user_chip, avatar_picker,
    pop_flash_success, flash_success, go_to_feed
)

st.header("👤 Profile")
user_chip()
pop_flash_success()

sb = get_supabase()
u = require_user()  # returns your existing users row {user_id, display_name, avatar_id, email, auth_id}

# fresh fetch (in case it changed)
row = (
    sb.table("users")
    .select("*")
    .eq("user_id", u["user_id"])
    .single()
    .execute()
    .data
    or {}
)

st.subheader("Account")
st.caption("Email is managed by Supabase Auth.")
st.text_input("Email", value=row.get("email", ""), disabled=True)

with st.expander("Change password", expanded=True):
    new_pw = st.text_input("New password", type="password", placeholder="At least 8 characters")
    confirm_pw = st.text_input("Confirm new password", type="password")
    if st.button("Update password"):
        if not new_pw or len(new_pw) < 8:
            st.error("Password must be at least 8 characters.")
        elif new_pw != confirm_pw:
            st.error("Passwords do not match.")
        else:
            try:
                sb.auth.update_user({"password": new_pw})
                st.success("Password updated.")
            except Exception as e:
                st.error(f"Failed to update password: {e}")

st.subheader("Profile")
display_name = st.text_input("Display Name", value=row.get("display_name", "") or "")
new_avatar = avatar_picker(key="profile_avatar", default=row.get("avatar_id"))

if st.button("Save profile"):
    updates = {
        "display_name": (display_name or row.get("display_name") or "").strip(),
        "avatar_id": new_avatar or row.get("avatar_id"),
    }
    try:
        sb.table("users").update(updates).eq("user_id", u["user_id"]).execute()
        # reflect in session row returned by require_user()
        u["display_name"] = updates["display_name"]
        u["avatar_id"] = updates["avatar_id"]
        flash_success("Profile updated.")
        st.rerun()
    except Exception as e:
        st.error(f"Could not update profile: {e}")
