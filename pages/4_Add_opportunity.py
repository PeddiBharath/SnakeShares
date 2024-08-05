import streamlit as st
from supabase import create_client
from concurrent.futures import ThreadPoolExecutor
from argon2 import PasswordHasher
from datetime import datetime,timezone
from misc_functions import is_valid_email

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
ph = PasswordHasher()

supabase = create_client(url, key)

st.title("To add new Opportunities")
st.markdown("**<span style='font-size:30px; color:red;'>Intended for Peddi Bharath</span>**", unsafe_allow_html=True)

def check_admin(email):
    result = supabase.table("admin").select("password").eq("email", email).execute()
    if result.data:
        return result.data[0]["password"]
    else:
        return None

def add_opportunity(name, url, details, tag):
    supabase.table("opportunities").insert({"name": name, "url": url, "details": details, "tag": tag}).execute()
    emailid = supabase.table("users").select("emailid").execute()
    created_at = datetime.now(timezone.utc).isoformat()
    for data in emailid.data:
        email = data['emailid']
        supabase.table("users_opportunities").insert({"name": name, "url" : url, "created_at" : created_at, "details": details, "tag" : tag, "email" : email, "status" : "unread"}).execute()

# Initialize session state for admin
if 'admin' not in st.session_state:
    st.session_state['admin'] = " "

if st.session_state['admin']==" ":
    tab1, = st.tabs(["Login"])
    with tab1:
        with st.form(key="bharath"):
            email = st.text_input(label="Enter email*")
            password = st.text_input(label="Enter password*",type="password"
            )
            submit = st.form_submit_button("Submit")
            if submit:
                if not email or not password:
                    st.warning("Enter all the mandatory fields")
                elif not is_valid_email(email):
                    st.error("Enter a proper email")
                else:
                    with ThreadPoolExecutor() as executor:
                        future = executor.submit(check_admin,email)
                        hashed_password = future.result()
                        try:
                            if (ph.verify(hashed_password, password)):
                                st.session_state['admin']="Authenticated"
                        except Exception as e:
                            st.warning("You might not be Peddi Bharath")
                        if(st.session_state['admin']=="Authenticated"):
                            st.rerun()
                        
                
if st.session_state['admin']=="Authenticated":
    with st.form(key="opportunity"):
        name=st.text_input("Name of the opportunity")
        url=st.text_input("Enter the url")
        details = st.text_area("Enter details")
        tag = st.selectbox(
                "Tag",
                ("BVRIT", "Jobs/Internships", "Hackathon/Competition"), key="tag_opportunity")
        submit = st.form_submit_button("Submit")

        if submit:
            with ThreadPoolExecutor() as executor:
                future = executor.submit(add_opportunity,name,url,details,tag)
                st.success("Opportunity added")
    
                    
