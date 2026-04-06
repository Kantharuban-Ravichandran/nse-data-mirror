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

    for i in range(7):
        while now.weekday() > 4:
            now = now - timedelta(days=1)
            
        dd = now.strftime("%d%m%y") # Format: 060426
        
        # New UDiFF style path (Price Reporting)
        # BCM = Bhav Copy Market
        url = f"https://archives.nseindia.com/content/indices/bhavcopy/cm{dd}bhav.zip"
        
        print(f"Trying New UDiFF Path: {now.strftime('%Y-%m-%d')} | URL: {url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*"
        }

        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    csv_filename = z.namelist()[0]
                    with z.open(csv_filename) as f:
                        data = f.read().decode('utf-8')
                        with open("latest_bhavcopy.csv", "w") as output:
                            output.write(data)
                print(f"✅ SUCCESS: Data found for {now.strftime('%Y-%m-%d')}")
                return 
            else:
                print(f"❌ Status {response.status_code}. Trying previous day...")
                now = now - timedelta(days=1)
        except Exception as e:
            print(f"⚠️ Error: {e}")
            now = now - timedelta(days=1)

    print("🚫 Could not find data.")
    exit(1)

if __name__ == "__main__":
    fetch_nse_bhavcopy()
