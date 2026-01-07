#!/usr/bin/env python3
"""
Simple test script for Dannazione di Providenza API
Run this while the main app is running to test the API endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_root():
    """Test root endpoint"""
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_config():
    """Test config endpoint"""
    print("Testing config endpoint...")
    response = requests.get(f"{BASE_URL}/config")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_ask():
    """Test ask endpoint"""
    print("Testing ask endpoint...")
    data = {
        "question": "What does 'Guten Morgen' mean?"
    }
    response = requests.post(f"{BASE_URL}/ask", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_screenshot():
    """Test screenshot endpoint"""
    print("Testing screenshot endpoint...")
    response = requests.post(f"{BASE_URL}/screenshot")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

if __name__ == "__main__":
    print("=== Dannazione di Providenza API Test ===\n")

    try:
        test_root()
        test_health()
        test_config()
        test_ask()
        test_screenshot()

        print("✓ All tests completed!")
    except requests.exceptions.ConnectionError:
        print("✗ Error: Cannot connect to API. Make sure the app is running.")
    except Exception as e:
        print(f"✗ Error: {e}")

