import streamlit as st
from common import get_supabase

st.header("Create Account")
email = st.text_input("Email")
pw = st.text_input("Password", type="password")

if st.button("Sign Up"):
    sb = get_supabase()
    try:
        sb.auth.sign_up({"email": email, "password": pw})
        st.success("Check your email to confirm your account, then sign in.")
    except Exception as e:
        st.error(f"Sign-up failed: {e}")
