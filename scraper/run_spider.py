#!/usr/bin/env python
"""
This file runs the properties_spider.py, saves the results to listings.json, and updates meta.json with statistics.
It is called by the Node.js API.
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta


DATA_DIR = Path(__file__).parent / "data"
LISTINGS_FILE = DATA_DIR / "listings.json"
TEMP_OUTPUT_FILE = DATA_DIR / "listings_temp.json"
META_FILE = DATA_DIR / "meta.json"

LOGS_DIR = Path(__file__).parent / "scraper" / "logs"

SPIDER_PATH = Path(__file__).parent / "scraper" / "spiders" / "properties_spider.py"

WORKING_DIR = Path(__file__).parent

script_start_time = datetime.now()

def run_spider():
    """Run the spider using scrapy runspider command."""
    output_file = LISTINGS_FILE
    
    # create the data directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # run scrapy command through a subprocess
    # Use uppercase -O to overwrite the temp file
    cmd = [
        "scrapy",
        "runspider",
        str(SPIDER_PATH),
        "-O", 
        str(TEMP_OUTPUT_FILE),
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(WORKING_DIR))
    
    if result.returncode == 0:
        # Spider completed successfully, now replace the actual file
        print("Spider completed successfully")
        # Replace the original file with the temp file only after spider finishes
        TEMP_OUTPUT_FILE.replace(output_file) # source.replace(target)
        update_meta_json()
        return True
    else:
        print(f"Spider failed with exit code {result.returncode}")
        # Clean up temp file if it exists
        if TEMP_OUTPUT_FILE.exists():
            TEMP_OUTPUT_FILE.unlink()
        return False


def update_meta_json():
    """Update meta.json with statistics from listings.json and logs from log file"""
    
    if not LISTINGS_FILE.exists():
        print("listings.json not found")
        return
    
    try:
        # Read listings.json
        with open(LISTINGS_FILE, 'r') as f:
            listings_data = json.load(f)
        
        # listings = listings_data.get('listings', [])
        
        # Calculate statistics
        prices = [
            item.get('price')
            for item in listings_data
            if item.get('price') is not None
        ]

        # Collect unique locations
        unique_locations = list({
            item.get("location")
            for item in listings_data
            if item.get("location")
        })
        
        # Read logs from the log file
        logs = {}
        log_file = LOGS_DIR / "spider.log"
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    spider_logs = f.read().strip().split('\n')
            except Exception as e:
                print(f"Error reading log file: {e}")
                spider_logs = []
        
        # Append scraping summary log
        # logs["scraping_time"] = datetime.now(timezone.utc).isoformat()
        logs["error_logs"] = [log for log in spider_logs if "ERROR" in log]
        logs["scraping_summary"] = f"Scraped {len(listings_data)} properties"

        
        process_end_time = datetime.now()
        # Create meta object
        meta = {
            "min_price": min(prices) if prices else None,
            "max_price": max(prices) if prices else None,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "scraping_duration": (  process_end_time - script_start_time).total_seconds(),
            "total_properties": len(listings_data),
            "logs": logs,
            "locations": unique_locations,
        }
        
        # Write meta.json
        with open(META_FILE, 'w') as f:
            json.dump(meta, f, indent=2)
        
        print(f"Updated meta.json")
        print(f"Total properties: {len(listings_data)}")
        print(f"Log entries: {len(logs)}")

        
    except Exception as e:
        print(f"Error updating meta.json: {e}")


if __name__ == "__main__":
    
    # call update_meta_json() instead if you don't want to scrape but just want to update the meta.json based on existing listings.json and logs
    run_spider()
    # update_meta_json()
    
    end_time = datetime.now()
    total_runtime = end_time - script_start_time

    print(f"\nStarted at: {script_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Ended at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total runtime: {total_runtime}\n")
