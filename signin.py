# Home.py
import streamlit as st
from common import sign_in, sign_up, current_user, user_chip, avatar_picker, go_to_feed

st.set_page_config(page_title="Home", page_icon="🏠")
st.header("🏠 Welcome to Offline Activity Tracker")
user_chip()

u = current_user()
if u:
    st.success(f"Signed in as {u['display_name']} ({u['user_id']})")
    if st.button("Go to Feed"):
        go_to_feed()
    st.stop()

tabs = st.tabs(["Sign In", "Sign Up"])

with tabs[0]:
    st.subheader("Sign In")
    uid = st.text_input("User ID", key="signin_uid")
    pwd = st.text_input("Password", type="password", key="signin_pwd")
    if st.button("Sign In"):
        ok, msg = sign_in(uid.strip(), pwd)
        if ok:
            st.success(msg)
            go_to_feed()
        else:
            st.error(msg)

with tabs[1]:
    st.subheader("Sign Up")
    su_uid = st.text_input("Choose a User ID")
    su_pwd = st.text_input("Password", type="password")
    su_name = st.text_input("Display Name")
    su_avatar = avatar_picker(key="signup_avatar")  # returns one of AVATAR_IDS
    if st.button("Create Account"):
        ok, msg = sign_up(su_uid.strip(), su_pwd.strip(), su_name.strip(), su_avatar)
        if ok:
            st.success(msg)
            go_to_feed()
        else:
            st.error(msg)
