import streamlit as st
from supabase import create_client
import re
import resend

# Initialize Supabase client and resend
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
resend.api_key = st.secrets["resend_broadcast"]
audience_id = st.secrets["audience_id"]

supabase = create_client(url, key)
# Email validation function
def is_valid_email(email):
    email_regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(email_regex, email)

#add old opportunities for new user and add to contacts of resend
def new_verified_user(email):
    response = supabase.table("opportunities").select("*").execute()
    datas = response.data
    check = supabase.table("users").select("*").eq("emailid", email).execute()
    if not check.data : 
        supabase.table("users").insert({"emailid":email}).execute()
        for data in datas:
            data["email"] = email
            data["status"] = "unread"
            supabase.table("users_opportunities").insert(data).execute()

        #resend broadcast
        params: resend.Contacts.CreateParams = {
            "email": st.session_state['email'],
            "audience_id": audience_id,
        }
        resend.Contacts.create(params)

