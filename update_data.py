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
    
    # --- UPDATED TIMING LOGIC ---
    # Based on your observation (8:50 PM), we set the cutoff to 8:00 PM (20:00).
    # If the script runs before 8:00 PM IST, it assumes today's data is not yet ready.
    if now.hour < 20:
        print("🕒 Pre-8:00 PM IST: Today's data likely not ready. Looking for yesterday's file...")
        now = now - timedelta(days=1)
    else:
        print("🕒 Post-8:00 PM IST: Attempting to fetch today's fresh data...")

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

    # Try last 7 days to find the most recent trading day
    for i in range(7):
        # Skip Sat/Sun logic
        while now.weekday() > 4: 
            now = now - timedelta(days=1)
            
        date_str = now.strftime("%d%m%y") # DDMMYY for URL
        url = f"https://nsearchives.nseindia.com/archives/equities/bhavcopy/pr/PR{date_str}.zip"
        
        print(f"🔍 Searching for Bhavcopy ZIP: PR{date_str}.zip...")
        
        try:
            response = session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    file_list = z.namelist()
                    
                    # Case-insensitive search for the 'pd' CSV file
                    target = next((f for f in file_list if f.lower().startswith('pd') and f.lower().endswith('.csv')), None)
                    
                    if not target:
                        csv_files = [info for info in z.infolist() if info.filename.lower().endswith('.csv')]
                        if csv_files:
                            target = max(csv_files, key=lambda x: x.file_size).filename

                    if target:
                        with z.open(target) as f:
                            content = f.read().decode('utf-8')
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
