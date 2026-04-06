import requests
import zipfile
import io
import os
from datetime import datetime, timedelta
import pytz

def fetch_nse_bhavcopy():
    # Set timezone to IST for accurate date calculation
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    # If it's before 6:30 PM IST, today's data might not be ready. Check yesterday.
    if now.hour < 18 or (now.hour == 18 and now.minute < 30):
        now = now - timedelta(days=1)

    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.nseindia.com/all-reports"
    }

    # "Wake up" the session by visiting the home page first
    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
    except:
        pass

    # Try last 7 days to find the most recent trading day (skips weekends/holidays)
    for i in range(7):
        while now.weekday() > 4: # Skip Sat/Sun
            now = now - timedelta(days=1)
            
        date_str = now.strftime("%d%m%y") # DDMMYY for URL
        url = f"https://nsearchives.nseindia.com/archives/equities/bhavcopy/pr/PR{date_str}.zip"
        
        print(f"🔍 Searching for Bhavcopy ZIP: PR{date_str}.zip...")
        
        try:
            response = session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    file_list = z.namelist()
                    
                    # CASE-INSENSITIVE SEARCH: Look for any file starting with 'pd' and ending in '.csv'
                    # NSE sometimes uses PD07042026.csv or pd07042026.csv
                    target = next((f for f in file_list if f.lower().startswith('pd') and f.lower().endswith('.csv')), None)
                    
                    # FALLBACK: If no 'pd' file, take the largest CSV in the zip (usually the main data)
                    if not target:
                        csv_files = [info for info in z.infolist() if info.filename.lower().endswith('.csv')]
                        if csv_files:
                            target = max(csv_files, key=lambda x: x.file_size).filename

                    if target:
                        with z.open(target) as f:
                            content = f.read().decode('utf-8')
                            # Overwrite the master file for GitHub to sync
                            with open("latest_bhavcopy.csv", "w", encoding='utf-8') as output:
                                output.write(content)
                        print(f"✅ SUCCESS: Extracted {target} as latest_bhavcopy.csv")
                        return 
            
            print(f"❌ No file found for {date_str}. Trying previous day...")
            now = now - timedelta(days=1)
        except Exception as e:
            print(f"⚠️ Error on {date_str}: {e}")
            now = now - timedelta(days=1)

    print("🚫 Critical Error: Could not find any valid NSE data in the last 7 days.")
    exit(1)

if __name__ == "__main__":
    fetch_nse_bhavcopy()
