import streamlit as st
from supabase import create_client
from misc_functions import is_valid_email, new_verified_user,unread_template, applied_template, ignored_template
from gotrue.errors import AuthApiError
from concurrent.futures import ThreadPoolExecutor

# Initialize Supabase client
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)

st.title("SnakeShares")

with st.expander('About this App'):
	st.markdown(
    """
    **Your Ultimate Job-Sharing Platform!** Stay updated with the latest job openings and effortlessly organize them into categories like:
    
    - **Unread/Unapplied**: Opportunities waiting for your attention
    - **Applied**: Jobs you've already sunk your teeth into
    - **Ignored**: Opportunities that you don't want to apply

    I apply for job opportunities often and will email you the positions I've applied to at the end of the day, but only if I’ve applied to any jobs.
    """
)

# Initialize session state for email
if 'email' not in st.session_state:
    st.session_state['email'] = " "

# Define function to run queries in parallel
def run_query(status, tag=None):
    query = supabase.table("users_opportunities").select("*").eq("email", email).eq("status", status)
    if tag:
        query = query.eq("tag", tag)
    query = query.order("created_at", desc=True)
    return query.execute()

# If user is not logged in, show Register/Login/Forgot Password tabs
if st.session_state['email'] == " ":
    tab1, tab2 = st.tabs(["Register", "Login"])
    
    # Register tab
    with tab1:
        with st.form(key="register"):
            email_id = st.text_input(label="Enter email* (If BVRIT student use bvrit email)", help="Enter your email")
            password = st.text_input(label="Enter password*", type="password", help="At least enter 6 characters")
            st.markdown("**required*")
            submit = st.form_submit_button("Submit")
            if submit:
                if not email_id or not password:
                    st.warning("Enter all the mandatory fields")
                elif not is_valid_email(email_id):
                    st.error("Enter a proper email")
                else:
                    try:
                        supabase.auth.sign_up({"email": email_id, "password": password})
                        st.success("Thanks for signing up! Check your email and confirm the email")
                    except Exception as e:
                        st.error(f"An unexpected error occurred during registration: {e}")

    # Login tab
    with tab2:
        with st.form(key="login"):
            email_id = st.text_input(label="Enter email* (If BVRIT student use bvrit email)", help="Enter your email")
            password = st.text_input(label="Enter password*", type="password", help="Enter the password used while registering")
            st.markdown("**required*")
            submit = st.form_submit_button("Submit")
            if submit:
                if not email_id or not password:
                    st.warning("Enter all the mandatory fields")
                elif not is_valid_email(email_id):
                    st.error("Enter a proper email")
                else:
                    try:
                        session = supabase.auth.sign_in_with_password({"email": email_id, "password": password})
                        st.session_state['email'] = email_id
                        # st.experimental_rerun()
                    except AuthApiError as e:
                        if "Email not confirmed" in str(e):
                            st.warning("Error: Email not confirmed. Please confirm your email before logging in.")
                        else:
                            st.warning(f"AuthApiError: {e}")
                    except Exception as e:
                        st.warning(f"An unexpected error occurred during login: {e}")
                    with ThreadPoolExecutor() as executor:
                        if not st.session_state['email']==" ":
                            future = executor.submit(new_verified_user,email_id)
                            future.result()
                    st.rerun()


else:
    m = st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: rgb(204, 49, 49);
        width: 100%; /* Default to full width */
        max-width: 700px; /* Maximum width */
        padding: 10px 20px;
        border: none;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 12px;
    }
    </style>""", unsafe_allow_html=True)

    email = st.session_state['email']

    tab1, tab2, tab3 = st.tabs(["Unread", "Applied", "UnInterested"])

    with ThreadPoolExecutor() as executor:
        # Unread tab
        with tab1:
            option = st.selectbox(
                "Type of opportunity",
                ("All", "Only from BVRIT", "Hackathons/Competitions", "Jobs/Internships"), key="tab1")
            
            if option == "All":
                future = executor.submit(run_query, "unread")
            elif option == "Only from BVRIT":
                future = executor.submit(run_query, "unread", "BVRIT")
            elif option == "Hackathons/Competitions":
                future = executor.submit(run_query, "unread", "Hackathon/Competition")
            elif option == "Jobs/Internships":
                future = executor.submit(run_query, "unread", "Jobs/Internships")

            rows = future.result()
            unread_template(rows)

        # Applied tab
        with tab2:
            option = st.selectbox(
                "Type of opportunity",
                ("All", "Only from BVRIT", "Hackathons/Competitions", "Jobs/Internships"), key="tab2")
            
            if option == "All":
                future = executor.submit(run_query, "applied")
            elif option == "Only from BVRIT":
                future = executor.submit(run_query, "applied", "BVRIT")
            elif option == "Hackathons/Competitions":
                future = executor.submit(run_query, "applied", "Hackathon/Competition")
            elif option == "Jobs/Internships":
                future = executor.submit(run_query, "applied", "Jobs/Internships")

            rows = future.result()
            applied_template(rows)

        # UnInterested tab
        with tab3:
            option = st.selectbox(
                "Type of opportunity",
                ("All", "Only from BVRIT", "Hackathons/Competitions", "Jobs/Internships"), key="tab3")
            
            if option == "All":
                future = executor.submit(run_query, "ignored")
            elif option == "Only from BVRIT":
                future = executor.submit(run_query, "ignored", "BVRIT")
            elif option == "Hackathons/Competitions":
                future = executor.submit(run_query, "ignored", "Hackathon/Competition")
            elif option == "Jobs/Internships":
                future = executor.submit(run_query, "ignored", "Jobs/Internships")

            rows = future.result()
            ignored_template(rows)
