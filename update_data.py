import requests
import zipfile
import io
from datetime import datetime, timedelta
import pytz

def fetch_nse_bhavcopy():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    # If before 6 PM, start looking from yesterday
    if now.hour < 18:
        now = now - timedelta(days=1)

    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.nseindia.com/all-reports"
    }

    for i in range(7):
        while now.weekday() > 4: # Skip Sat/Sun
            now = now - timedelta(days=1)
            
        # Format: 06-Apr-2026
        dd = now.strftime("%d")
        mmm = now.strftime("%b").upper()
        yyyy = now.strftime("%Y")
        
        # CORRECT EQUITIES ARCHIVE PATH
        # Note the folder is 'historical/EQUITIES' and filename is 'cm...bhav.csv.zip'
        url = f"https://archives.nseindia.com/content/historical/EQUITIES/{yyyy}/{mmm}/cm{dd}{mmm}{yyyy}bhav.csv.zip"
        
        print(f"🔍 Checking Equities Archive: {now.strftime('%Y-%m-%d')} | URL: {url}")
        
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
            print(f"⚠️ Error: {e}")
            now = now - timedelta(days=1)

    print("🚫 All attempts failed. Manual check required.")
    exit(1)

if __name__ == "__main__":
    fetch_nse_bhavcopy()
