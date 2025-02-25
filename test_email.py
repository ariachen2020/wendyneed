from email_sender import EmailSender
import logging
import os
from dotenv import load_dotenv

# 設置詳細的日誌記錄
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_email_sender():
    try:
        # 載入環境變數
        load_dotenv()
        
        # 檢查環境變數
        api_key = os.getenv('SENDGRID_API_KEY')
        from_email = os.getenv('SENDGRID_FROM_EMAIL')
        
        logging.info("檢查環境變數...")
        if not api_key:
            logging.error("找不到 SENDGRID_API_KEY")
            return False
        if not from_email:
            logging.error("找不到 SENDGRID_FROM_EMAIL")
            return False
            
        logging.info(f"使用發件人郵箱: {from_email}")
        
        # 創建 EmailSender 實例
        sender = EmailSender()
        
        # 發送測試郵件
        test_recipient = input("請輸入測試用的收件人郵箱地址: ")
        
        result = sender.send_email(
            test_recipient,
            "SendGrid 測試郵件",
            "這是一封測試郵件，用於確認 SendGrid 設置是否正確。"
        )
        
        if result:
            logging.info("測試郵件發送成功！")
        else:
            logging.error("測試郵件發送失敗。")
            
        return result
        
    except Exception as e:
        logging.error(f"測試過程中發生錯誤: {str(e)}")
        logging.error("詳細錯誤信息:", exc_info=True)
        return False

if __name__ == "__main__":
    print("開始測試 SendGrid 郵件發送...")
    success = test_email_sender()
    print("\n測試結果:", "成功" if success else "失敗") 