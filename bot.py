import os
import requests
import yfinance as yf

CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_TOKEN")
USER_ID = "U218ad9e5b909ea9dd6edc7b0d6f6c622"

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
  alert_messages = []
  for ticker, target_price in target_stocks.items():
    try:
      stock = yf.Ticker(ticker)
      df = stock.history(period="1d")
      if not df.empty:
        current_price = round(df["Close"].iloc[-1], 2)
        print(f"{ticker}: {current_price} (เป้าหมาย <= {target_price})")
        if current_price <= target_price:
          alert_messages.append(
              f"🚨 แจ้งเตือน! {ticker} ราคาลงมาอยู่ที่ {current_price}"
              f" (ถึงเป้า <= {target_price})"
          )
    except Exception as e:
      print(f"เกิดข้อผิดพลาด {ticker}: {e}")

  if alert_messages:
    full_message = "📉 สรุปหุ้นที่ถึงราคาเป้าหมาย:\n\n" + "\n".join(
        alert_messages
    )
    send_line_message(full_message)
    print("ส่งแจ้งเตือนเข้า LINE แล้ว")
  else:
    send_line_message(
        "🤖 บอทเช็คราคาหุ้นรอบนี้: ยังไม่มีหุ้นตัวไหนถึงราคาเป้าหมายครับ"
    )
    print("ส่งรายงานสถานะปกติเข้า LINE แล้ว")


if __name__ == "__main__":
  check_stock_prices()
