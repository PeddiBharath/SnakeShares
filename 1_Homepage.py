import streamlit as st

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

