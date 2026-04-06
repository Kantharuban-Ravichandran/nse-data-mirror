import requests
import zipfile
import io
import os
from datetime import datetime, timedelta
import pytz

def fetch_nse_bhavcopy():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    if now.hour < 18:
        now = now - timedelta(days=1)

    # We use a session to handle cookies automatically
    session = requests.Session()
    
    # Headers to make the bot look like a real Chrome browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.nseindia.com/all-reports"
    }

    # Step 1: Visit the main page to get necessary cookies
    try:
        session.get("https://www.nseindia.com/all-reports", headers=headers, timeout=10)
    except Exception as e:
        print(f"Initial connection failed: {e}")

    for i in range(7):
        while now.weekday() > 4:
            now = now - timedelta(days=1)
            
        date_str = now.strftime("%d-%b-%Y") # Format: 06-Apr-2026
        
        # This is the actual API URL NSE uses for the UDiFF Bhavcopy
        url = f"https://www.nseindia.com/api/reports?archives=[%7B%22name%22:%22cm-udiff-common-bhavcopy-final%22,%22type%22:%22daily%22,%22category%22:%22equities%22,%22date%22:%22{date_str}%22%7D]&type=equities&mode=single"
        
        print(f"Checking Date: {date_str}")
        
        try:
            response = session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200 and len(response.content) > 1000:
                # The response is a ZIP file
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    csv_filename = z.namelist()[0]
                    with z.open(csv_filename) as f:
                        data = f.read().decode('utf-8')
                        with open("latest_bhavcopy.csv", "w") as output:
                            output.write(data)
                print(f"✅ SUCCESS: Data found for {date_str}")
                return 
            else:
                print(f"❌ No data for {date_str} (Status: {response.status_code}).")
                now = now - timedelta(days=1)
        except Exception as e:
            print(f"⚠️ Error on {date_str}: {e}")
            now = now - timedelta(days=1)

    print("🚫 Checked last 7 days. Markets might be closed or API changed.")
    exit(1)

if __name__ == "__main__":
    fetch_nse_bhavcopy()
