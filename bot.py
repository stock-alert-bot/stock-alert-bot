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
    report = "📈 สรุปราคาหุ้นล่าสุด (นอกเวลาทำการ):\n"
    alert_triggered = False
    
    for ticker, target_price in target_stocks.items():
        current_price = None
        try:
            stock = yf.Ticker(ticker)
            
            # ลำดับที่ 1: ดึงจาก info ดึง currentPrice หรือ regularMarketPrice
            try:
                info = stock.info
                current_price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("regularMarketPreviousClose")
            except Exception:
                pass
            
            # ลำดับที่ 2: ถ้ายังไม่ได้ ให้ลองดึงจาก fast_info
            if current_price is None or str(current_price) == 'nan':
                if hasattr(stock, "fast_info") and "lastPrice" in stock.fast_info:
                    current_price = stock.fast_info["lastPrice"]
            
            # ลำดับที่ 3: ถ้ายังไม่ได้อีก ให้ดึงจากประวัติล่าสุด .history()
            if current_price is None or str(current_price) == 'nan':
                hist = stock.history(period="1d")
                if not hist.empty and 'Close' in hist.columns:
                    current_price = hist['Close'].dropna().iloc[-1]

            # แปลงและตรวจสอบค่า
            if current_price is not None and str(current_price) != 'nan':
                price_val = float(current_price)
                if price_val <= target_price:
                    report += f"🚨 - {ticker}: {price_val:.2f} (ถึงเป้า <= {target_price} แล้ว!)\n"
                    alert_triggered = True
                else:
                    report += f"- {ticker}: {price_val:.2f} (เป้า: {target_price})\n"
            else:
                report += f"- {ticker}: ไม่พบข้อมูลราคา\n"
                
        except Exception as e:
            report += f"- {ticker}: เกิดข้อผิดพลาด\n"
            
    if alert_triggered:
        report = "⚠️ **แจ้งเตือน! ราคาหุ้นเข้าเป้าแล้ว** ⚠️\n\n" + report

    send_line_message(report)

if __name__ == "__main__":
    check_stock_prices()
    
