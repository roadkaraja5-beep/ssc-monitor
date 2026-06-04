import os
import requests
from bs4 import BeautifulSoup

# GitHub Secrets se tokens lena
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
URL = "https://ssc.gov.in"

def send_telegram_message(message):
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown", "disable_web_page_preview": False}
    try:
        requests.post(telegram_url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

def check_ssc():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(URL, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print("SSC Website open nahi ho rahi.")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # SSC ki website se saare meaningful notice links nikalna
        notices = []
        for link in soup.find_all('a'):
            text = link.text.strip()
            href = link.get('href', '')
            
            # Filter lagana taaki faltu links chhut jayein aur sirf exam/notice ke PDFs aayein
            if len(text) > 20 and ('pdf' in href.lower() or 'document' in href.lower() or 'notices' in href.lower() or 'portal' in href.lower()):
                if not href.startswith('http'):
                    href = URL + href
                if {"title": text, "link": href} not in notices:
                    notices.append({"title": text, "link": href})

        if not notices:
            print("Koi notice nahi mila. Website ka structure change ho sakta hai.")
            return

        # Latest notice ko select karna
        latest_notice = notices[0]
        latest_title = latest_notice['title']
        latest_link = latest_notice['link']

        # Purane notice ka cache file (`last_notice.txt`) check karna
        db_file = "last_notice.txt"
        old_title = ""
        
        if os.path.exists(db_file):
            with open(db_file, "r", encoding="utf-8") as f:
                old_title = f.read().strip()

        # Agar website par jo sabse upar notice hai, wo purane wale se alag hai toh message bhejein
        if latest_title != old_title:
            message = f"🚨 *New SSC Notice Alert!*\n\n📌 *📢 Notice:* {latest_title}\n\n🔗 *Link:* [Yahan Click Karein]({latest_link})"
            send_telegram_message(message)
            
            # Naye notice ka title save kar dena taaki agle 30 min me fir se same message na aaye
            with open(db_file, "w", encoding="utf-8") as f:
                f.write(latest_title)
            print("Naya notice mila aur message bhej diya gaya.")
        else:
            print("Koi naya notice nahi aaya, sab purana hi hai.")

    except Exception as e:
        print(f"Error aaya: {e}")

if __name__ == "__main__":
    check_ssc()
    
