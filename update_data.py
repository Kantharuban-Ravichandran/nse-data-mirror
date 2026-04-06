import requests
import zipfile
import io
import os
from datetime import datetime, timedelta
import pytz

def fetch_nse_bhavcopy():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    # Start checking from yesterday if before 6 PM
    if now.hour < 18:
        now = now - timedelta(days=1)

    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Referer": "https://www.nseindia.com/"
    }

    # First, "hit" the home page to get valid session cookies
    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
    except:
        pass

    for i in range(7):
        while now.weekday() > 4: # Skip Sat/Sun
            now = now - timedelta(days=1)
            
        # Format: 060426 (DDMMYY)
        date_str = now.strftime("%d%m%y")
        
        # This is the "Direct Archive" path for the consolidated bhavcopy
        url = f"https://archives.nseindia.com/content/indices/bhavcopy/cm{date_str}bhav.zip"
        
        print(f"🔍 Checking Archive: {now.strftime('%Y-%m-%d')} | URL: {url}")
        
        try:
            response = session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    csv_filename = z.namelist()[0]
                    with z.open(csv_filename) as f:
                        content = f.read().decode('utf-8')
                        with open("latest_bhavcopy.csv", "w") as output:
                            output.write(content)
                print(f"✅ SUCCESS: Data saved for {now.strftime('%Y-%m-%d')}")
                return 
            else:
                print(f"❌ Status {response.status_code}. Moving to previous day.")
                now = now - timedelta(days=1)
        except Exception as e:
            print(f"⚠️ Request Error: {e}")
            now = now - timedelta(days=1)

    print("🚫 All attempts failed. NSE might have changed the path again.")
    exit(1)

if __name__ == "__main__":
    fetch_nse_bhavcopy()
