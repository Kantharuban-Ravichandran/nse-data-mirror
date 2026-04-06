import requests
import zipfile
import io
import os
from datetime import datetime
import pytz

def fetch_nse_bhavcopy():
    # Set timezone to IST
    ist = pytz.timezone('Asia/Kolkata')
    # now = datetime.now(ist)
    now = datetime(2026, 4, 6, tzinfo=ist)
    
    # Format: cm22MAY2024bhav.csv.zip
    dd = now.strftime("%d")
    mmm = now.strftime("%b").upper()
    yyyy = now.strftime("%Y")
    
    filename = f"cm{dd}{mmm}{yyyy}bhav.csv"
    url = f"https://archives.nseindia.com/content/historical/EQUITIES/{yyyy}/{mmm}/{filename}.zip"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print(f"Attempting to fetch: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                # Extract the CSV and rename it to a constant name for Apps Script
                csv_filename = z.namelist()[0]
                with z.open(csv_filename) as f:
                    data = f.read().decode('utf-8')
                    with open("latest_bhavcopy.csv", "w") as output:
                        output.write(data)
            print("Successfully updated latest_bhavcopy.csv")
        else:
            print(f"Failed to fetch. Status code: {response.status_code}. Markets might be closed.")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    fetch_nse_bhavcopy()
