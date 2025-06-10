#!/usr/bin/env python3
"""
Script to get authentication cookie from OpenUI frontend at localhost:7878
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json


def get_openui_cookie():
    """Get authentication cookie from OpenUI frontend"""
    
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Comment out the headless option so we can see what's happening
    # chrome_options.add_argument("--headless")
    
    try:
        # Initialize the driver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Navigate to OpenUI
        print("Navigating to OpenUI at localhost:7878...")
        driver.get("http://localhost:7878")
        
        # Wait a bit for the page to load
        time.sleep(3)
        
        # Get all cookies
        cookies = driver.get_cookies()
        print(f"Found {len(cookies)} cookies")
        
        # Print cookies for debugging
        for cookie in cookies:
            print(f"Cookie: {cookie['name']} = {cookie['value']}")
        
        # Look for session or auth cookies
        auth_cookies = {}
        for cookie in cookies:
            # Common authentication cookie names
            if any(keyword in cookie['name'].lower() for keyword in ['session', 'auth', 'token', 'login']):
                auth_cookies[cookie['name']] = cookie['value']
        
        if not auth_cookies:
            # If no obvious auth cookies, take all cookies
            auth_cookies = {cookie['name']: cookie['value'] for cookie in cookies}
        
        # Save cookies to file
        with open('openui_cookies.json', 'w') as f:
            json.dump(auth_cookies, f, indent=2)
        
        print(f"Saved cookies to openui_cookies.json")
        print(f"Auth cookies: {auth_cookies}")
        
        return auth_cookies
        
    except Exception as e:
        print(f"Error getting cookies: {e}")
        return None
    finally:
        if 'driver' in locals():
            driver.quit()


if __name__ == "__main__":
    cookies = get_openui_cookie()
    if cookies:
        print("Successfully retrieved cookies!")
    else:
        print("Failed to retrieve cookies.")