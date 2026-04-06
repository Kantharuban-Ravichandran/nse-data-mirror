import requests
import zipfile
import io
import os
from datetime import datetime, timedelta
import pytz

def fetch_nse_bhavcopy():
    # Set timezone to IST for accurate market day calculation
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    # If before 6:30 PM IST, today's file might not be ready; check yesterday
    if now.hour < 18 or (now.hour == 18 and now.minute < 30):
        now = now - timedelta(days=1)

    session = requests.Session()
    # Verified headers to mimic a real browser session
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.nseindia.com/all-reports",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    }

    # Initialize cookies by visiting the main page
    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
    except:
        pass

    # Search back up to 7 days to account for weekends/holidays
    for i in range(7):
        while now.weekday() > 4: # Skip Saturday (5) and Sunday (6)
            now = now - timedelta(days=1)
            
        date_str = now.strftime("%d%m%y") # Format: DDMMYY (e.g., 060426)
        
        # verified URL path from your network snoop
        url = f"https://nsearchives.nseindia.com/archives/equities/bhavcopy/pr/PR{date_str}.zip"
        
        print(f"🔍 Attempting to fetch: {now.strftime('%Y-%m-%d')} | URL: {url}")
        
        try:
            response = session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    # SPECIFIC FILTER: Look for the file containing the actual price data
                    # This avoids the "Corporate Actions" file we accidentally caught earlier
                    target_file = next((f for f in z.namelist() if "BhavCopy_NSE_CM" in f and f.endswith('.csv')), None)
                    
                    if target_file:
                        with z.open(target_file) as f:
                            content = f.read().decode('utf-8')
                            with open("latest_bhavcopy.csv", "w") as output:
                                output.write(content)
                        print(f"✅ SUCCESS: Extracted the REAL Bhavcopy: {target_file}")
                        return 
                    else:
                        print(f"⚠️ Found ZIP but {target_file} not inside. Checking previous day.")
                        now = now - timedelta(days=1)
            else:
                print(f"❌ Status {response.status_code}. Market might have been closed.")
                now = now - timedelta(days=1)
        except Exception as e:
            print(f"⚠️ Error: {e}")
            now = now - timedelta(days=1)

    print("🚫 FAILURE: Could not find the price data in the last 7 days.")
    exit(1)

if __name__ == "__main__":
    fetch_nse_bhavcopy()
