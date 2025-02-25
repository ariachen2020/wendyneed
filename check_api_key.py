import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)

def check_api_key():
    load_dotenv()
    api_key = os.getenv('SENDGRID_API_KEY')
    
    if not api_key:
        print("錯誤：找不到 SENDGRID_API_KEY")
        return
        
    print("\nAPI Key 前六個字符:", api_key[:6])
    print("API Key 長度:", len(api_key))
    
    if not api_key.startswith('SG.'):
        print("警告：API Key 應該以 'SG.' 開頭")
    
    if len(api_key) < 50:
        print("警告：API Key 似乎太短了")

if __name__ == "__main__":
    print("檢查 SendGrid API Key...")
    check_api_key() 