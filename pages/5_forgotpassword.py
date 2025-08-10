import streamlit as st
from common import get_supabase

st.header("🔑 Forgot Password")
email = st.text_input("Email")

if st.button("Send reset link"):
    sb = get_supabase()
    try:
        sb.auth.reset_password_for_email(
            email,
            options={"redirect_to": st.secrets["APP_BASE_URL"] + "/Reset_Password"}
        )
    except Exception:
        pass
    st.success("If that email exists, a reset link has been sent.")
