import streamlit as st
import json
import re
from pathlib import Path
from email_sender import send_test_email
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_config():
    config_file = Path("config.json")
    if config_file.exists():
        with open(config_file, "r") as f:
            return json.load(f)
    return {"email": "", "target_rate": 0.0, "condition": "greater than or equal to"}

def save_config(email, target_rate, condition):
    config = {
        "email": email,
        "target_rate": target_rate,
        "condition": condition
    }
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

# Page configuration
st.set_page_config(
    page_title="Interest Rate Monitor",
    page_icon="📈",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
    }
    .main {
        padding: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("Interest Rate Monitor 📈")
st.markdown("""
Monitor Treasury rates and receive email notifications when your target conditions are met.
""")
st.markdown("---")

# Load existing configuration
config = load_config()

# Create two columns for the form
col1, col2 = st.columns(2)

with col1:
    # Input fields with validation
    email = st.text_input("Email Address", value=config["email"])
    target_rate = st.number_input(
        "Target Interest Rate (%)", 
        value=float(config["target_rate"]),
        min_value=0.0,
        max_value=100.0,
        step=0.1
    )

with col2:
    condition = st.selectbox(
        "Alert Condition",
        options=["greater than or equal to", "less than or equal to"],
        index=0 if config["condition"] == "greater than or equal to" else 1
    )
    
    # Test email button
    if st.button("Test Email Configuration"):
        if not email:
            st.error("Please enter an email address first")
        elif not is_valid_email(email):
            st.error("Please enter a valid email address")
        else:
            with st.spinner("Sending test email..."):
                if send_test_email(email):
                    st.success("Test email sent successfully! Please check your inbox.")
                else:
                    st.error("Failed to send test email. Please check the logs.")

# Save button with validation
if st.button("Save Configuration"):
    if not email:
        st.error("Please enter an email address")
    elif not is_valid_email(email):
        st.error("Please enter a valid email address")
    else:
        save_config(email, target_rate, condition)
        st.success("Configuration saved successfully! ✅")
        st.info("You will receive email notifications when your conditions are met.")

# Current rate display
try:
    import yfinance as yf
    tnx = yf.Ticker("^TNX")
    current_rate = tnx.info.get('regularMarketPrice')
    if current_rate is not None:
        st.metric(
            label="Current 10-Year Treasury Rate",
            value=f"{current_rate:.2f}%"
        )
except Exception:
    st.warning("Unable to fetch current rate. Please try again later.")

# Help section
with st.expander("ℹ️ How it works"):
    st.markdown("""
    1. Enter your email address for notifications
    2. Set your target interest rate
    3. Choose when you want to be notified
    4. Click Save to update your settings
    
    The system checks rates hourly and will notify you when conditions are met.
    
    **Note**: Make sure to check your spam folder if you don't receive notifications.
    """)

# System status
with st.expander("🔧 System Status"):
    st.markdown("""
    - **Monitoring**: Active (checking hourly)
    - **Email Service**: Connected to Gmail SMTP
    - **Data Storage**: Local JSON configuration
    """) 