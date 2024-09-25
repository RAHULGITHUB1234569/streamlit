import streamlit as st
import os
import json
from datetime import datetime
import pandas as pd
import plotly.express as px

# Directory for storing credentials
credentials_dir = os.path.join(os.getcwd(), "credentials")
os.makedirs(credentials_dir, exist_ok=True)

# File path for storing user data
file_path = os.path.join(credentials_dir, "user_data.json")

# Function to load user data from the JSON file
def load_user_data():
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return []

# Function to save user data to the JSON file
def save_user_data(user_data):
    with open(file_path, 'w') as file:
        json.dump(user_data, file, indent=4)

# Function to check if the email exists
def email_exists(email):
    user_data = load_user_data()
    return any(user["email"] == email for user in user_data)

# Function to verify login credentials
def verify_login(email, password):
    user_data = load_user_data()
    return any(user["email"] == email and user["password"] == password for user in user_data)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.email = ""

# Sidebar navigation based on the user's login status
st.sidebar.title("Navigation")

if st.session_state.logged_in:
    navigation = st.sidebar.radio("Go to", ["Home"])
else:
    navigation = st.sidebar.radio("Go to", ["Sign Up", "Login"])

# Sign-Up Page
if navigation == "Sign Up":
    st.title('Sign Up to Your Journey')
    st.header("Create Your Account")

    # Input fields for user data
    name = st.text_input("Name")
    phone = st.text_input("Phone Number")
    dob = st.date_input("Date of Birth", min_value=datetime(1900, 1, 1), max_value=datetime.now())
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    # Submit button
    if st.button("Sign Up"):
        if name and phone and dob and email and password:
            if email_exists(email):
                st.error("Email already exists. Please use a different email.")
            else:
                user_data = load_user_data()
                user_data.append({
                    "name": name,
                    "phone": phone,
                    "dob": str(dob),
                    "email": email,
                    "password": password
                })
                save_user_data(user_data)
                st.success("Sign-up successful! Redirecting to the login page...")
                st.session_state.logged_in = False  # Ensure the user is not logged in yet
                st.session_state.email = email  # Store the email for later use
                st.rerun()  # Rerun to navigate to login page
        else:
            st.error("Please fill in all the fields.")

# Login Page
elif navigation == "Login":
    st.title('Login to Your Account')

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if verify_login(email, password):
            st.session_state.logged_in = True
            st.session_state.email = email
            st.success("Login successful! Redirecting to Home page...")
            st.rerun()
        else:
            st.error("Invalid email or password.")

# Home Page (after successful login)
elif navigation == "Home":
    email = st.session_state.email
    st.title(f"Welcome to the Homepage, {email}!")

    # Collect marks for at least 7 subjects
    subjects = ["Maths", "Science", "English", "History", "Geography", "Physics", "Chemistry"]
    marks = {}

    for subject in subjects:
        marks[subject] = st.slider(f"Choose your marks for {subject}", 0, 100, 50)

    if st.button("Submit"):
        user_folder = os.path.join(credentials_dir, email)
        os.makedirs(user_folder, exist_ok=True)
        marks_df = pd.DataFrame(list(marks.items()), columns=["Subject", "Marks"])
        csv_file = os.path.join(user_folder, "marks.csv")
        marks_df.to_csv(csv_file, index=False)
        st.success("Marks submitted successfully!")

        # Display charts using Plotly
        st.header("Your Reports are Ready!")
        st.subheader("Average Marks Chart")
        bar_fig = px.bar(marks_df, x="Subject", y="Marks", title="Marks per Subject")
        st.plotly_chart(bar_fig)

        st.subheader("Marks as per each subject - Line Graph")
        line_fig = px.line(marks_df, x="Subject", y="Marks", title="Marks per Subject (Line Graph)")
        st.plotly_chart(line_fig)

        st.subheader("Marks as per each subject - Pie Chart")
        pie_fig = px.pie(marks_df, names="Subject", values="Marks", title="Marks Distribution")
        st.plotly_chart(pie_fig)

    # Sign Out button in sidebar
    if st.sidebar.button("Sign Out"):
        st.session_state.logged_in = False
        st.session_state.email = ""
        st.success("You have been signed out successfully. Redirecting to login page...")
        st.rerun()
