import requests
import zipfile
import io
import os
from datetime import datetime, timedelta
import pytz

def fetch_nse_bhavcopy():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    # If before 6 PM IST, look for yesterday's data
    if now.hour < 18:
        now = now - timedelta(days=1)

    session = requests.Session()
    # Using the exact headers required for the nsearchives server
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.nseindia.com/all-reports",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    }

    # Step 1: Initialize session with a visit to the main site
    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
    except:
        pass

    # Search back up to 7 days
    for i in range(7):
        while now.weekday() > 4: # Skip Sat/Sun
            now = now - timedelta(days=1)
            
        # Format: DDMMYY (e.g., 060426)
        date_str = now.strftime("%d%m%y")
        
        # THE VERIFIED URL FROM YOUR SNOOP
        url = f"https://nsearchives.nseindia.com/archives/equities/bhavcopy/pr/PR{date_str}.zip"
        
        print(f"🚀 Fetching PR Bhavcopy: {now.strftime('%Y-%m-%d')} | URL: {url}")
        
        try:
            response = session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    # PR zip files usually contain multiple files; we want the .csv
                    csv_files = [f for f in z.namelist() if f.endswith('.csv')]
                    if csv_files:
                        with z.open(csv_files[0]) as f:
                            content = f.read().decode('utf-8')
                            with open("latest_bhavcopy.csv", "w") as output:
                                output.write(content)
                        print(f"✅ SUCCESS: Saved data for {now.strftime('%Y-%m-%d')}")
                        return 
            else:
                print(f"❌ Status {response.status_code} for {date_str}. Trying previous day...")
                now = now - timedelta(days=1)
        except Exception as e:
            print(f"⚠️ Error: {e}")
            now = now - timedelta(days=1)

    print("🚫 Failed to find PR Bhavcopy in the last 7 days.")
    exit(1)

if __name__ == "__main__":
    fetch_nse_bhavcopy()
