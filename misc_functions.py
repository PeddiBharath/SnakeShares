import streamlit as st
from supabase import create_client
import re
import resend
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

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


# Define dialog functions
@st.dialog("Opportunity")
def unread(id, name, url, details):
    st.markdown(f"""
        <style>
            .opp-name {{
                font-size: 20px;
                font-weight: bold;
            }}
        </style>
        <div class="opp-name">{name}</div>
    """, unsafe_allow_html=True)
    st.markdown(details)
    st.markdown(f"To know more visit: [Apply Here]({url})")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Move to Applied"):
            with ThreadPoolExecutor() as executor:
                future = executor.submit(update_status, id, "applied")
                future.result()
            st.rerun()
    with col2:
        if st.button("Ignore it"):
            with ThreadPoolExecutor() as executor:
                future = executor.submit(update_status, id, "ignored")
                future.result()
            st.rerun()

@st.dialog("Opportunity")
def applied(id, name, url, details):
    st.markdown(f"""
        <style>
            .opp-name {{
                font-size: 20px;
                font-weight: bold;
            }}
        </style>
        <div class="opp-name">{name}</div>
    """, unsafe_allow_html=True)
    st.markdown(details)
    st.markdown(f"To know more visit: [Apply Here]({url})")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Move to Unread"):
            with ThreadPoolExecutor() as executor:
                future = executor.submit(update_status, id, "unread")
                future.result()
            st.rerun()
    with col2:
        if st.button("Ignore it"):
            with ThreadPoolExecutor() as executor:
                future = executor.submit(update_status, id, "ignored")
                future.result()
            st.rerun()

@st.dialog("Opportunity")
def ignored(id, name, url, details):
    st.markdown(f"""
        <style>
            .opp-name {{
                font-size: 20px;
                font-weight: bold;
            }}
        </style>
        <div class="opp-name">{name}</div>
    """, unsafe_allow_html=True)
    st.markdown(details)
    st.markdown(f"To know more visit: [Apply Here]({url})")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Move to Unread"):
            with ThreadPoolExecutor() as executor:
                future = executor.submit(update_status, id, "unread")
                future.result()
            st.rerun()
    with col2:
        if st.button("Move to Applied"):
            with ThreadPoolExecutor() as executor:
                future = executor.submit(update_status, id, "applied")
                future.result()
            st.rerun()


# Function to update status in Supabase
def update_status(id, status):
    supabase.table("users_opportunities").update({"status": status}).eq("id", id).execute()

# Define time range for filtering
seven_days_ago = datetime.now() - timedelta(days=7)
seven_days_ago_str = seven_days_ago.strftime('%Y-%m-%d %H:%M:%S.%f')

# Define template functions
def unread_template(rows):
    st.markdown("<hr>", unsafe_allow_html=True)
    st.write("New Opportunities")
    for row in rows.data:
        if row['created_at'] >= seven_days_ago_str:
            if st.button(row['name'], key=row['created_at']):
                unread(row['id'], row['name'], row['url'], row['details'])
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.write("Older than 7 days")
    for row in rows.data:
        if row['created_at'] < seven_days_ago_str:
            if st.button(row['name'], key=row['created_at']):
                unread(row['id'], row['name'], row['url'], row['details'])

def applied_template(rows):
    st.markdown("<hr>", unsafe_allow_html=True)
    st.write("New Opportunities")
    for row in rows.data:
        if row['created_at'] >= seven_days_ago_str:
            if st.button(row['name'], key=row['created_at']):
                applied(row['id'], row['name'], row['url'], row['details'])
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.write("Older than 7 days")
    for row in rows.data:
        if row['created_at'] < seven_days_ago_str:
            if st.button(row['name'], key=row['created_at']):
                applied(row['id'], row['name'], row['url'], row['details'])

def ignored_template(rows):
    st.markdown("<hr>", unsafe_allow_html=True)
    st.write("New Opportunities")
    for row in rows.data:
        if row['created_at'] >= seven_days_ago_str:
            if st.button(row['name'], key=row['created_at']):
                ignored(row['id'], row['name'], row['url'], row['details'])
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.write("Older than 7 days")
    for row in rows.data:
        if row['created_at'] < seven_days_ago_str:
            if st.button(row['name'], key=row['created_at']):
                ignored(row['id'], row['name'], row['url'], row['details'])
