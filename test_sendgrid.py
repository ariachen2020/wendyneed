from email_sender import EmailSender
import logging

# 設置詳細的日誌記錄
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_send_email():
    try:
        # 創建 EmailSender 實例
        sender = EmailSender()
        
        # 發送測試郵件
        result = sender.send_email(
            to_email="aria@arialifetalk.com",
            subject="利率監控系統測試郵件",
            body="""
            您好，

            這是一封測試郵件，用於確認利率監控系統的郵件發送功能是否正常。

            如果您收到這封郵件，表示系統設置正確。

            祝好，
            利率監控系統
            """
        )
        
        if result:
            print("✅ 測試郵件發送成功！")
            print("請檢查收件箱 aria@arialifetalk.com")
        else:
            print("❌ 測試郵件發送失敗")
            
    except Exception as e:
        print(f"❌ 發生錯誤: {str(e)}")
        logging.error("詳細錯誤信息:", exc_info=True)

if __name__ == "__main__":
    print("開始測試 SendGrid 郵件發送...")
    test_send_email() 