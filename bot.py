import os
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://ssc.gov.in/"

def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text
        }
    )

def get_latest_notice():
    r = requests.get(URL, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    text = soup.get_text(" ", strip=True)

    return text[:5000]

def main():
    current = get_latest_notice()

    try:
        with open("last_notice.txt", "r", encoding="utf-8") as f:
            old = f.read()
    except:
        old = ""

    if old == "":
        with open("last_notice.txt", "w", encoding="utf-8") as f:
            f.write(current)

        send_message("✅ SSC Monitor Started Successfully")
        return

    if current != old:
        send_message("🚨 SSC Website Updated!\nhttps://ssc.gov.in")

        with open("last_notice.txt", "w", encoding="utf-8") as f:
            f.write(current)

if __name__ == "__main__":
    main()
