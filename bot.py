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
    report = "📈 สรุปราคาปัจจุบัน/ล่าสุด:\n"
    alert_triggered = False
    
    for ticker, target_price in target_stocks.items():
        current_price = None
        try:
            stock = yf.Ticker(ticker)
            
            # ลำดับที่ 1: ดึงผ่าน fast_info["lastPrice"] (จะได้ราคาปัจจุบันหรือราคาอัปเดตล่าสุด ณ ขณะนั้นทันที)
            try:
                if hasattr(stock, "fast_info") and "lastPrice" in stock.fast_info:
                    val = stock.fast_info["lastPrice"]
                    if val is not None:
                        current_price = float(val)
            except Exception:
                pass
            
            # ลำดับที่ 2: ถ้าวิธีแรกไม่ได้ ให้ดึงจาก info (currentPrice หรือ regularMarketPrice)
            if current_price is None or str(current_price) == 'nan':
                info = stock.info
                val = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("regularMarketPreviousClose")
                if val is not None:
                    current_price = float(val)

            # ลำดับที่ 3: สำรองสุดท้าย ใช้ประวัติรายวัน .history()
            if current_price is None or str(current_price) == 'nan':
                hist = stock.history(period="1d")
                if not hist.empty and 'Close' in hist.columns:
                    val = hist['Close'].dropna().iloc[-1]
                    if val is not None:
                        current_price = float(val)

            # ตรวจสอบผลลัพธ์และส่งค่าออกเป็นตัวเลข
            if current_price is not None and str(current_price) != 'nan':
                if current_price <= target_price:
                    report += f"🚨 - {ticker}: {current_price:.2f} (ถึงเป้า <= {target_price} แล้ว!)\n"
                    alert_triggered = True
                else:
                    report += f"- {ticker}: {current_price:.2f} (เป้า: {target_price})\n"
            else:
                report += f"- {ticker}: ไม่พบข้อมูลราคา\n"
                
        except Exception as e:
            report += f"- {ticker}: เกิดข้อผิดพลาด\n"
            
    if alert_triggered:
        report = "⚠️ **แจ้งเตือน! ราคาหุ้นเข้าเป้าแล้ว** ⚠️\n\n" + report

    send_line_message(report)

if __name__ == "__main__":
    check_stock_prices()
