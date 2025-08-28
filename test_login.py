#!/usr/bin/env python3
"""
Test script to debug login issues
"""

import requests
import json

def test_login():
    """Test the login functionality"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Login System...")
    print("=" * 40)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Server is running (Status: {response.status_code})")
        print(f"   Redirected to: {response.url}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:5000")
        return
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return
    
    # Test 2: Test login page
    try:
        response = requests.get(f"{base_url}/login")
        print(f"✅ Login page accessible (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error accessing login page: {e}")
        return
    
    # Test 3: Test login with correct credentials
    print("\n🔐 Testing login with correct credentials...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        session = requests.Session()
        response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        print(f"   Login response status: {response.status_code}")
        
        if response.status_code == 302:  # Redirect
            print(f"   Redirected to: {response.headers.get('Location', 'Unknown')}")
            
            # Follow redirect to see if we get to homepage
            redirect_response = session.get(f"{base_url}{response.headers.get('Location', '')}")
            print(f"   Redirect response status: {redirect_response.status_code}")
            
            if "Welcome" in redirect_response.text:
                print("✅ Login successful! Redirected to homepage.")
            else:
                print("⚠️  Login redirected but homepage content unclear.")
        else:
            print(f"   Unexpected response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error during login test: {e}")
    
    # Test 4: Test login with wrong credentials
    print("\n❌ Testing login with wrong credentials...")
    wrong_data = {
        'username': 'admin',
        'password': 'wrongpassword'
    }
    
    try:
        response = requests.post(f"{base_url}/login", data=wrong_data, allow_redirects=False)
        print(f"   Wrong credentials response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Correctly stayed on login page with wrong credentials")
        else:
            print(f"   Unexpected response with wrong credentials: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during wrong credentials test: {e}")
    
    print("\n" + "=" * 40)
    print("🏁 Login test completed!")

if __name__ == "__main__":
    test_login() 