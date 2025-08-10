# pages/4_Profile.py
import streamlit as st
from common import get_supabase, require_user, user_chip, avatar_picker, encode_password

st.header("👤 Profile")
user_chip()

u = require_user()
sb = get_supabase()

row = sb.table("users").select("*").eq("user_id", u["user_id"]).single().execute().data

display_name = st.text_input("Display Name", value=row.get("display_name",""))
password = st.text_input("New Password", value="enter new password")
new_avatar = avatar_picker(key="profile_avatar", default=row.get("avatar_id"))

if st.button("Save Changes"):
    updates = {"display_name": display_name.strip() or row.get("display_name")}
    updates["avatar_id"] = new_avatar
    if password!="" and password!="enter new password":
        updates["password_hash"] = encode_password(password)
    sb.table("users").update(updates).eq("user_id", u["user_id"]).execute()
    # refresh session
    u["display_name"] = updates["display_name"]
    u["avatar_id"] = new_avatar
    st.success("Profile updated.")
