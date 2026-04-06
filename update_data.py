import requests
import zipfile
import io
import os
from datetime import datetime, timedelta
import pytz

def fetch_nse_bhavcopy():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    # If before 6:30 PM IST, today's data likely isn't posted; check yesterday
    if now.hour < 18 or (now.hour == 18 and now.minute < 30):
        now = now - timedelta(days=1)

    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.nseindia.com/all-reports"
    }

    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
    except:
        pass

    for i in range(7):
        while now.weekday() > 4:
            now = now - timedelta(days=1)
            
        date_str = now.strftime("%d%m%y")
        full_date_str = now.strftime("%d%m%Y") # For the internal filename pdDDMMYYYY.csv
        url = f"https://nsearchives.nseindia.com/archives/equities/bhavcopy/pr/PR{date_str}.zip"
        
        print(f"🔍 Checking PR Zip for {now.strftime('%Y-%m-%d')}...")
        
        try:
            response = session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    file_list = z.namelist()
                    
                    # Target 1: pdddmmyyyy.csv (Symbols + Prices)
                    target = f"pd{full_date_str}.csv"
                    
                    # Target 2: If naming is slightly different, look for any file starting with 'pd'
                    if target not in file_list:
                        target = next((f for f in file_list if f.startswith('pd') and f.endswith('.csv')), None)
                    
                    # Target 3: Safety fallback to the largest file (usually the main Bhavcopy)
                    if not target:
                        csv_info = [info for info in z.infolist() if info.filename.endswith('.csv')]
                        if csv_info:
                            target = max(csv_info, key=lambda x: x.file_size).filename

                    if target:
                        with z.open(target) as f:
                            content = f.read().decode('utf-8')
                            with open("latest_bhavcopy.csv", "w") as output:
                                output.write(content)
                        print(f"✅ SUCCESS: Extracted {target} as your master data.")
                        return 
            
            print(f"❌ No data for {date_str}. Trying previous day...")
            now = now - timedelta(days=1)
        except Exception as e:
            print(f"⚠️ Error: {e}")
            now = now - timedelta(days=1)

    print("🚫 All attempts failed.")
    exit(1)

if __name__ == "__main__":
    fetch_nse_bhavcopy()
