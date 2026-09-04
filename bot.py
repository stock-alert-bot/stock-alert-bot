import os
import requests
import yfinance as yf

# ดึงค่า Token จาก GitHub Secrets ที่ตั้งชื่อว่า LINE_TOKEN
CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_TOKEN")
# ใส่ User ID ของคุณสำหรับรับข้อความ
USER_ID = "Ub3a230a9ffbfcb174e17cfd01dd3cbd6"

# กำหนดหุ้นและราคาเป้าหมายสำหรับแจ้งเตือน (ซื้อเมื่อราคาต่ำกว่าหรือเท่ากับเป้า)
target_stocks = {
    "VOO": 705,
    "MSFT": 499,
    "NVDA": 215,
    "GOOGL": 339,
    "AVGO": 253,
    "VXUS": 87,  # เพิ่ม VXUS ที่ราคาเป้าหมาย 87
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
    report = "📈 สรุปราคาหุ้น (ราคาปัจจุบัน/ล่าสุด):\n"
    alert_triggered = False
    
    for ticker, target_price in target_stocks.items():
        try:
            stock = yf.Ticker(ticker)
            current_price = None
            
            # วิธีที่ 1: ดึงผ่าน fast_info เพื่อดูราคาล่าสุด (รองรับราคานอกเวลาทำการ)
            try:
                if hasattr(stock, "fast_info") and "lastPrice" in stock.fast_info:
                    current_price = stock.fast_info["lastPrice"]
            except Exception:
                pass
            
            # วิธีที่ 2: ถ้าวิธีแรกไม่ได้ผล ให้ลองดึงผ่าน info
            if current_price is None:
                info = stock.info
                current_price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")

            # วิธีที่ 3: สำรองสุดท้าย ใช้ .history()
            if current_price is None:
                todays_data = stock.history(period="1d")
                if not todays_data.empty:
                    current_price = todays_data['Close'].iloc[-1]

            if current_price is not None:
                # เช็กเงื่อนไข: ถ้าราคาปัจจุบัน <= ราคาเป้าหมาย ให้แจ้งเตือนพิเศษ
                if current_price <= target_price:
                    report += f"🚨 - {ticker}: {current_price:.2f} (ถึงเป้า <= {target_price} แล้ว!)\n"
                    alert_triggered = True
                else:
                    report += f"- {ticker}: {current_price:.2f} (เป้า: {target_price})\n"
            else:
                report += f"- {ticker}: ไม่พบข้อมูลราคา\n"
                
        except Exception as e:
            report += f"- {ticker}: เกิดข้อผิดพลาด\n"
            
    # สามารถเพิ่มข้อความหัวข้อเตือนพิเศษด้านบนได้หากมีตัวที่ถึงเป้า
    if alert_triggered:
        report = "⚠️ **แจ้งเตือน! มีหุ้นราคาเข้าเป้าแล้ว** ⚠️\n\n" + report

    send_line_message(report)

if __name__ == "__main__":
    check_stock_prices()
