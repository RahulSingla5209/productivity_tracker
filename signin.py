import streamlit as st
from common import get_supabase, go_to_feed

st.header("Sign In")
email = st.text_input("Email")
pw = st.text_input("Password", type="password")

if st.button("Sign In"):
    sb = get_supabase()
    try:
        sb.auth.sign_in_with_password({"email": email, "password": pw})
        go_to_feed()
    except Exception as e:
        st.error(f"Could not sign in: {e}")

st.page_link("pages/0_signup.py", label="Create account", icon="➕")
st.page_link("pages/5_forgotpassword.py", label="Forgot password?", icon="🔑")
