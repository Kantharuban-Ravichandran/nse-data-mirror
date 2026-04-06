import requests
import zipfile
import io
import os
from datetime import datetime, timedelta
import pytz

def fetch_nse_bhavcopy():
    # 1. Set timezone to IST
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    # 2. Logic: If running before 6:00 PM IST, the today's file isn't ready.
    # We look for yesterday's file instead.
    if now.hour < 18:
        now = now - timedelta(days=1)
    
    # 3. Weekend Check: If 'now' is Sat(5) or Sun(6), go back to Friday(4)
    while now.weekday() > 4: 
        now = now - timedelta(days=1)
        
    # 4. Format the URL components
    dd = now.strftime("%d")
    mmm = now.strftime("%b").upper()
    yyyy = now.strftime("%Y")
    
    # Example format: cm06APR2026bhav.csv.zip
    filename = f"cm{dd}{mmm}{yyyy}bhav.csv"
    url = f"https://archives.nseindia.com/content/historical/EQUITIES/{yyyy}/{mmm}/{filename}.zip"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print(f"Target Date: {now.strftime('%Y-%m-%d')}")
    print(f"Attempting to fetch: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                # Extract the CSV
                csv_filename = z.namelist()[0]
                with z.open(csv_filename) as f:
                    data = f.read().decode('utf-8')
                    # Save with a consistent name for Google Apps Script to find
                    with open("latest_bhavcopy.csv", "w") as output:
                        output.write(data)
            print("✅ Successfully updated latest_bhavcopy.csv")
        else:
            print(f"❌ Failed to fetch. Status code: {response.status_code}.")
            print("Note: If it's a market holiday, the file won't exist.")
            # Ensure the process fails so GitHub Action doesn't try to 'git add' nothing
            exit(1) 
    except Exception as e:
        print(f"⚠️ Error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    fetch_nse_bhavcopy()
