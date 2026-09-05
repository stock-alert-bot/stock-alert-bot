import os
import json
from datetime import datetime
import requests
import yfinance as yf

# ดึงค่า Token จาก GitHub Secrets
CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_TOKEN")
USER_ID = "Ub3a230a9ffbfcb174e17cfd01dd3cbd6"

STATE_FILE = "stock_state.json"

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
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print("ส่งข้อความสำเร็จ:", response.json())
    except requests.exceptions.RequestException as e:
        print(f"เกิดข้อผิดพลาดในการส่ง LINE API: {e}")

def load_state():
    """โหลดข้อมูลสถานะการแจ้งเตือนของวันจากไฟล์ JSON"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_state(state):
    """บันทึกสถานะลงไฟล์ JSON"""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=4)

def check_stock_prices():
    today_str = datetime.now().strftime("%Y-%m-%d")
    state = load_state()
    
    # ถ้าขึ้นวันใหม่แล้ว ให้รีเซ็ตประวัติการแจ้งเตือนของวันเก่าทิ้ง
    if state.get("date") != today_str:
        state = {"date": today_str, "alerted_stocks": []}

    already_alerted_today = state.get("alerted_stocks", [])
    
    report = "📈 สรุปราคา Pre-market (ณ ตอนนี้):\n"
    alert_triggered = False
    new_alerts_this_round = []
    
    for ticker, target_price in target_stocks.items():
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # ลำดับที่ 1: ดึงราคา Pre-market หรือ Post-market สดๆ
            current_price = info.get("preMarketPrice") or info.get("postMarketPrice")
            
            # ลำดับที่ 2: ถ้าไม่มี ให้ดึง currentPrice หรือ regularMarketPrice
            if current_price is None or str(current_price) == 'nan':
                current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            
            # ลำดับที่ 3: สำรองสุดท้าย ใช้ราคาปิดเดิม
            if current_price is None or str(current_price) == 'nan':
                current_price = info.get("regularMarketPreviousClose") or info.get("previousClose")

            # ตรวจสอบและแสดงผลเป็นตัวเลข
            if current_price is not None and str(current_price) != 'nan':
                price_val = float(current_price)
                if price_val <= target_price:
                    report += f"🚨 - {ticker}: {price_val:.2f} (ถึงเป้า <= {target_price} แล้ว!)\n"
                    
                    # เช็คว่าตัวนี้เคยแจ้งเตือนไปแล้วหรือยังใน "วันนี้"
                    if ticker not in already_alerted_today:
                        alert_triggered = True
                        new_alerts_this_round.append(ticker)
                else:
                    report += f"- {ticker}: {price_val:.2f} (เป้า: {target_price})\n"
            else:
                report += f"- {ticker}: ไม่พบข้อมูลราคา\n"
                
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            report += f"- {ticker}: เกิดข้อผิดพลาด\n"
            
    # ส่งข้อความเฉพาะเมื่อมีหุ้นตัว "ใหม่" ที่เพิ่งเข้าเป้าในรอบนี้
    if alert_triggered:
        final_report = "⚠️ **แจ้งเตือน! ราคาหุ้นเข้าเป้าแล้ว** ⚠️\n\n" + report
        send_line_message(final_report)
        
        # บันทึกว่าหุ้นเหล่านี้ถูกแจ้งเตือนไปแล้วในวันนี้
        state["alerted_stocks"] = already_alerted_today + new_alerts_this_round
        save_state(state)
    else:
        print("ไม่มีหุ้นเข้าเป้ารอบใหม่ หรือเคยแจ้งเตือนไปหมดแล้วสำหรับวันนี้")

if __name__ == "__main__":
    check_stock_prices()
