import yfinance as yf
import json
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv
from email_sender import EmailSender
import requests

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('interest_monitor.log'),
        logging.StreamHandler()
    ]
)

def load_config():
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            # Validate required fields
            required_fields = ['email', 'target_rate', 'condition']
            if not all(field in config for field in required_fields):
                raise ValueError("Missing required fields in config.json")
            return config
    except FileNotFoundError:
        logging.error("config.json not found")
        return None
    except (json.JSONDecodeError, ValueError) as e:
        logging.error(f"Configuration error: {str(e)}")
        return None

def get_current_rate(max_retries=2, base_delay=30):
    """
    從 FRED 獲取當前利率，使用緩存機制
    """
    # 首先檢查緩存
    cache_file = "rate_cache.json"
    try:
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                cache_data = json.load(f)
                cache_time = datetime.fromisoformat(cache_data['timestamp'])
                # 如果緩存時間不超過15分鐘，直接使用緩存數據
                if datetime.now() - cache_time < timedelta(minutes=15):
                    logging.info(f"使用緩存的利率數據: {cache_data['rate']}%")
                    return cache_data['rate']
    except Exception as e:
        logging.warning(f"讀取緩存失敗: {str(e)}")

    def _get_rate_from_fred():
        """從 FRED API 獲取利率"""
        try:
            # FRED API endpoint
            url = "https://api.stlouisfed.org/fred/series/observations"
            params = {
                'series_id': 'DGS10',  # 10-Year Treasury Rate
                'api_key': os.getenv('FRED_API_KEY'),
                'sort_order': 'desc',
                'limit': 1,
                'file_type': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('observations') and len(data['observations']) > 0:
                    rate = float(data['observations'][0]['value'])
                    logging.info(f"從 FRED 成功獲取利率: {rate}%")
                    
                    # 保存到緩存
                    cache_data = {
                        'rate': rate,
                        'timestamp': datetime.now().isoformat(),
                        'source': 'FRED'
                    }
                    try:
                        with open(cache_file, "w") as f:
                            json.dump(cache_data, f)
                    except Exception as e:
                        logging.warning(f"保存緩存失敗: {str(e)}")
                        
                    return rate
            else:
                logging.error(f"FRED API 返回錯誤狀態碼: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logging.error(f"FRED API 請求失敗: {str(e)}")
        except (ValueError, KeyError) as e:
            logging.error(f"解析 FRED 數據失敗: {str(e)}")
        except Exception as e:
            logging.error(f"從 FRED 獲取數據時發生未知錯誤: {str(e)}")
        return None

    # 嘗試從 FRED 獲取數據
    for attempt in range(max_retries):
        if attempt > 0:
            logging.info(f"等待 {base_delay} 秒後進行第 {attempt + 1} 次嘗試...")
            time.sleep(base_delay)
            
        rate = _get_rate_from_fred()
        if rate is not None:
            return rate

    logging.error("無法從 FRED 獲取利率數據")
    return None

def check_condition(current_rate, target_rate, condition):
    if condition == "greater than or equal to":
        return current_rate >= target_rate
    elif condition == "less than or equal to":
        return current_rate <= target_rate
    else:
        logging.error(f"Invalid condition: {condition}")
        return False

def send_rate_notification(recipient, current_rate, target_rate, condition):
    try:
        sender = EmailSender()
        subject = f"Interest Rate Alert - {current_rate:.2f}%"
        body = f"""
        Interest Rate Alert!
        
        Current 10-Year Treasury Rate: {current_rate:.2f}%
        Your Target Rate: {target_rate:.2f}%
        Condition: {condition}
        
        This notification was triggered because the current rate is {condition} your target rate.
        
        You can update your preferences at any time through the Interest Rate Monitor interface.
        """
        
        return sender.send_email(recipient, subject, body)
    
    except Exception as e:
        logging.error(f"Error sending rate notification: {str(e)}")
        return False

def main():
    # Load configuration
    config = load_config()
    if not config:
        return

    # Get current rate
    current_rate = get_current_rate()
    if current_rate is None:
        return

    logging.info(f"Current 10-Year Treasury Rate: {current_rate}%")

    # Check if conditions are met
    if check_condition(current_rate, config['target_rate'], config['condition']):
        logging.info("Target condition met - sending notification")
        send_rate_notification(
            config['email'],
            current_rate,
            config['target_rate'],
            config['condition']
        )
    else:
        logging.info("Target condition not met - no notification needed")

if __name__ == "__main__":
    main() 