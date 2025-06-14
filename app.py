import requests
from bs4 import BeautifulSoup
import time
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
from dotenv import load_dotenv
import os

# --- CONFIGURATION ---

PRODUCTS = {
    "Macaron": "https://www.popmart.com/us/products/675/THE-MONSTERS---Exciting-Macaron-Vinyl-Face-Blind-Box",
    "Have a Seat": "https://www.popmart.com/us/products/1372/THE-MONSTERS---Have-a-Seat-Vinyl-Plush-Blind-Box",
    "Big into Energy": "https://www.popmart.com/us/products/2155/THE-MONSTERS-Big-into-Energy-Series-Vinyl-Plush-Pendant-Blind-Box"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

CHECK_INTERVAL = 60  # seconds between checks

# --- EMAIL SETUP ---
load_dotenv()
EMAIL_FROM = os.getenv("EMAIL_FROM_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_FROM_PASS")
EMAIL_TO = os.getenv("EMAIL_TO_USER")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# --- TWILIO SETUP ---
TWILIO_SID = os.get("SID")
TWILIO_AUTH = os.get("AUTH_TOKEN")
TWILIO_FROM = os.get("Number")  # Twilio number
TWILIO_TO = os.get("MY_NUMBER")    # Your phone number

# --- FUNCTIONS ---

def is_in_stock(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        add_bag = soup.find('button', text=lambda t: t and "Add to Cart" in t)
        return add_bag not in soup.text
    except Exception as e:
        print("Error:", e)
        return False

def send_email(subject, body):
    msg = MIMEText(body)
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg['Subject'] = subject

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

def send_sms(body):
    client = Client(TWILIO_SID, TWILIO_AUTH)
    client.messages.create(
        body=body,
        from_=TWILIO_FROM,
        to=TWILIO_TO
    )

# --- MAIN LOOP ---
print("🔍 Starting POP MART stock checker...")

while True:
    for name, link in PRODUCTS.items():
        if is_in_stock(link):
            message = f"🎉 '{name}' is now in stock at {link}"
            print(message)
            send_email(f"{name} is in stock!", message)
            send_sms(message)
            exit()  # or continue to check the next item
        else:
            print(f"❌ '{name}' is still out of stock.")
    time.sleep(CHECK_INTERVAL)
