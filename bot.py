import os
import requests
import yfinance as yf

# ดึงค่า Token จาก GitHub Secrets ที่ตั้งชื่อว่า LINE_TOKEN
CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_TOKEN")
# ใส่ User ID ของคุณสำหรับรับข้อความ
USER_ID = "Ub3a230a9ffbfcb174e17cfd01dd3cbd6"

target_stocks = {
    "VOO": 705,
    "MSFT": 499,
    "NVDA": 215,
    "GOOGL": 339,
    "AVGO": 253,
    "VXUS": 87,
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
    report = "📈 สรุปราคาปิดตลาดล่าสุด:\n"
    alert_triggered = False
    
    for ticker, target_price in target_stocks.items():
        try:
            stock = yf.Ticker(ticker)
            closing_price = None
            
            # ดึงข้อมูลราคาย้อนหลังรายวัน (เอาแท่งล่าสุดที่ตลาดปิดไปแล้ว)
            hist = stock.history(period="2d")
            if not hist.empty:
                # ใช้ราคา Close ของแถวสุดท้ายที่มีการบันทึก (ราคาปิดของรอบล่าสุด)
                closing_price = hist['Close'].iloc[-1]
            
            # ถ้าดึงจาก history ไม่ได้ ให้สำรองใช้ regularMarketPreviousClose หรือ previousClose จาก info
            if closing_price is None:
                info = stock.info
                closing_price = info.get("regularMarketPreviousClose") or info.get("previousClose")

            if closing_price is not None:
                # เช็กเงื่อนไข: ถ้าราคาปิด <= ราคาเป้าหมาย
                if closing_price <= target_price:
                    report += f"🚨 - {ticker}: {closing_price:.2f} (ถึงเป้า <= {target_price} แล้ว!)\n"
                    alert_triggered = True
                else:
                    report += f"- {ticker}: {closing_price:.2f} (เป้า: {target_price})\n"
            else:
                report += f"- {ticker}: ไม่พบข้อมูลราคาปิด\n"
                
        except Exception as e:
            report += f"- {ticker}: เกิดข้อผิดพลาด\n"
            
    if alert_triggered:
        report = "⚠️ **แจ้งเตือน! ราคาปิดตลาดเข้าเป้าแล้ว** ⚠️\n\n" + report

    send_line_message(report)

if __name__ == "__main__":
    check_stock_prices()
