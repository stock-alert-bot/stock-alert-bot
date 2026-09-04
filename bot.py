import os
import requests
import yfinance as yf

# ดึงค่า Token จาก GitHub Secrets ที่ตั้งชื่อว่า LINE_TOKEN
CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_TOKEN")
# ใส่ User ID ของคุณสำหรับรับข้อความ (หรือเปลี่ยนเป็นรหัสผู้ใช้ของคุณ)
USER_ID = "y/RaGyzitie+yUKCZcOvafLsnoAEFx/LFcm6iN2w4VQ2C0VSCymHxnw06KENeia6egWk"
    "JuvvLsyCTAKZfJKUp6SgWMQ915pcNvR1DdImJelwy4yLIEgyO1bLs0JuFemkjS2zLG9E"
    "yv1lAXCaLeO+AdB04t89/1O/w1cDnylFU="

target_stocks = {
    "VOO": 705,
    "MSFT": 499,
    "NVDA": 215,
    "GOOGL": 339,
    "AVGO": 253,
}

def send_line_message(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    }
    data = {
        "to": USER_ID,
        "messages": [{"type": "text", "text": message}],
    }
    response = requests.post(url, headers=headers, json=data)
    print(response.json())

def check_stock_prices():
    report = "📈 สรุปราคาราคาหุ้น:\n"
    for ticker, target_price in target_stocks.items():
        try:
            stock = yf.Ticker(ticker)
            # ดึงราคาปัจจุบัน
            todays_data = stock.history(period="1d")
            if not todays_data.empty:
                current_price = todays_data['Close'].iloc[-1]
                report += f"- {ticker}: {current_price:.2f} (เป้า: {target_price})\n"
            else:
                report += f"- {ticker}: ไม่พบข้อมูลราคา\n"
        except Exception as e:
            report += f"- {ticker}: เกิดข้อผิดพลาด\n"
            
    send_line_message(report)

if __name__ == "__main__":
    check_stock_prices()
