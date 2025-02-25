import json
import logging
import os
from datetime import datetime
from email_sender import EmailSender
from pathlib import Path
import requests
from dotenv import load_dotenv

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_current_rate():
    """從 FRED API 獲取當前利率"""
    try:
        # 載入環境變數
        load_dotenv()
        api_key = os.getenv('FRED_API_KEY')
        
        if not api_key:
            logging.error("找不到 FRED API Key")
            return None
            
        logging.info("正在從 FRED 獲取利率數據...")
        
        # FRED API endpoint
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            'series_id': 'DGS10',  # 10-Year Treasury Rate
            'api_key': api_key,
            'sort_order': 'desc',
            'limit': 1,
            'file_type': 'json'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('observations') and len(data['observations']) > 0:
                # 檢查是否有有效數據
                value = data['observations'][0]['value']
                if value != '.':  # FRED 有時會用 '.' 表示缺失數據
                    rate = float(value)
                    logging.info(f"當前利率: {rate}%")
                    return rate
                else:
                    logging.warning("FRED 返回了缺失數據")
            else:
                logging.warning("FRED 返回的數據格式不符合預期")
        else:
            logging.error(f"FRED API 請求失敗: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        logging.error(f"請求異常: {str(e)}")
    except ValueError as e:
        logging.error(f"數據解析錯誤: {str(e)}")
    except Exception as e:
        logging.error(f"獲取利率時發生未知錯誤: {str(e)}")
        
    return None

def check_conditions(current_rate, target_rate, condition):
    """檢查是否達到通知條件"""
    if condition == "greater than or equal to":
        return current_rate >= target_rate
    elif condition == "less than or equal to":
        return current_rate <= target_rate
    return False

def main():
    try:
        # 讀取配置
        config_path = Path("config.json")
        if not config_path.exists():
            logging.error("找不到配置文件 config.json")
            return
            
        with open(config_path, "r") as f:
            config = json.load(f)
            
        # 檢查配置
        required_fields = ["email", "target_rate", "condition"]
        for field in required_fields:
            if field not in config:
                logging.error(f"配置文件缺少必要字段: {field}")
                return
                
        logging.info(f"目標郵箱: {config['email']}")
        logging.info(f"目標利率: {config['target_rate']}%")
        logging.info(f"條件: {config['condition']}")
        
        # 獲取當前利率
        current_rate = get_current_rate()
        if current_rate is None:
            logging.error("無法獲取當前利率，監控終止")
            return

        # 檢查條件
        condition_met = check_conditions(current_rate, config["target_rate"], config["condition"])
        logging.info(f"條件是否達成: {condition_met}")
        
        if condition_met:
            # 發送通知
            try:
                sender = EmailSender()
                subject = f"利率監控通知 - 目標條件已達成"
                body = f"""
                您好，

                當前利率已達到您設定的條件：

                當前利率：{current_rate}%
                目標利率：{config['target_rate']}%
                條件：{config['condition']}

                時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

                此致，
                利率監控系統
                """
                
                result = sender.send_email(config["email"], subject, body)
                if result:
                    logging.info(f"通知郵件已成功發送至 {config['email']}")
                else:
                    logging.error("通知郵件發送失敗")
                    
            except Exception as e:
                logging.error(f"發送通知時發生錯誤: {str(e)}")
        else:
            logging.info("條件未達成，不發送通知")

    except json.JSONDecodeError as e:
        logging.error(f"配置文件格式錯誤: {str(e)}")
    except Exception as e:
        logging.error(f"監控過程中發生未知錯誤: {str(e)}")

if __name__ == "__main__":
    logging.info("=== 利率監控系統啟動 ===")
    main()
    logging.info("=== 監控完成 ===") 