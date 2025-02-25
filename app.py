import streamlit as st
import json
import re
from pathlib import Path
from email_sender import send_test_email
import os
from dotenv import load_dotenv
import random
import string
from datetime import datetime

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

# 生成隨機 key
def random_key(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

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
    /* 禁用自動填充 */
    input[type="text"], input[type="email"] {
        autocomplete: "off" !important;
        autocorrect: "off" !important;
        autocapitalize: "off" !important;
        spellcheck: "false" !important;
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
    # 使用動態 key 和空初始值
    email_key = f"email_input_{datetime.now().timestamp()}_{random_key()}"
    email = st.text_input(
        "Email Address", 
        value="",  # 始終使用空字符串作為初始值
        key=email_key,
        help="Enter your email address to receive notifications"
    )
    
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
    import requests
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    fred_api_key = os.getenv('FRED_API_KEY')
    
    if fred_api_key:
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            'series_id': 'DGS10',  # 10-Year Treasury Rate
            'api_key': fred_api_key,
            'sort_order': 'desc',
            'limit': 1,
            'file_type': 'json'
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('observations') and len(data['observations']) > 0:
                value = data['observations'][0]['value']
                if value != '.':
                    current_rate = float(value)
                    st.metric(
                        label="Current 10-Year Treasury Rate",
                        value=f"{current_rate:.2f}%"
                    )
    else:
        # 顯示一個更友好的訊息，並提供解決方案
        st.info("⚠️ Current rate display is disabled. API key not configured in this environment.")
        st.markdown("""
        **Note**: The current rate display is only available in the monitoring system, not in the web interface.
        Your rate monitoring will still work as scheduled.
        """)
except Exception as e:
    st.info(f"Current rate display is disabled in this environment.")

# Help section
with st.expander("ℹ️ How it works"):
    st.markdown("""
    1. Enter your email address for notifications
    2. Set your target interest rate
    3. Choose when you want to be notified
    4. Click Save to update your settings
    
    The system checks rates daily and will notify you when conditions are met.
    
    **Note**: Make sure to check your spam folder if you don't receive notifications.
    """)

# System status
with st.expander("🔧 System Status"):
    st.markdown("""
    - **Monitoring**: Active (checking daily)
    - **Email Service**: Connected to SendGrid
    - **Data Source**: FRED (Federal Reserve Economic Data)
    """) 