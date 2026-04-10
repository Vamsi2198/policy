import streamlit as st
import requests

# Replace with your actual local IP and port
API_URL = "http://192.168.67.96:5000/api/process"

st.title("Atlan Actions Governance Frontend")

command = st.text_input("Enter governance command:")

if st.button("Submit"):
    if command:
        response = requests.post(API_URL, json={"command": command})
        if response.ok:
            st.json(response.json())
        else:
            st.error(f"API error: {response.text}")
    else:
        st.warning("Please enter a command.")
