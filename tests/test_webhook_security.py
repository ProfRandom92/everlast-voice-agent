#!/usr/bin/env python3
"""
Test script for Vapi Webhook Security
Tests the x-vapi-secret header verification
"""

import os
import sys
import httpx
import asyncio

# Set test environment variables
os.environ['VAPI_SERVER_SECRET'] = 'test-secret-123'
os.environ['SUPABASE_URL'] = 'http://localhost'
os.environ['SUPABASE_SERVICE_KEY'] = 'test'
os.environ['ANTHROPIC_API_KEY'] = 'test-key'

# Add parent dir to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_webhook_security():
    """Test the webhook security headers"""

    print("=" * 60)
    print("VAPI WEBHOOK SECURITY TESTS")
    print("=" * 60)

    test_payload = {
        "message": {"role": "user", "content": "Test message"},
        "call": {"id": "test-123", "customer": {"number": "+49123456789"}}
    }

    # Test 1: Request without secret header
    print("\n[TEST 1] Request WITHOUT x-vapi-secret header")
    print("-" * 60)
    response = client.post("/vapi/webhook", json=test_payload)
    print(f"Status Code: {response.status_code}")
    print(f"Expected: 401")
    print(f"Result: {'✅ PASS' if response.status_code == 401 else '❌ FAIL'}")
    if response.status_code == 401:
        print(f"Response: {response.json()}")

    # Test 2: Request with wrong secret
    print("\n[TEST 2] Request with WRONG x-vapi-secret header")
    print("-" * 60)
    response = client.post(
        "/vapi/webhook",
        json=test_payload,
        headers={"x-vapi-secret": "wrong-secret"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Expected: 401")
    print(f"Result: {'✅ PASS' if response.status_code == 401 else '❌ FAIL'}")
    if response.status_code == 401:
        print(f"Response: {response.json()}")

    # Test 3: Request with correct secret
    print("\n[TEST 3] Request with CORRECT x-vapi-secret header")
    print("-" * 60)
    response = client.post(
        "/vapi/webhook",
        json=test_payload,
        headers={"x-vapi-secret": "test-secret-123"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Expected: 200")
    print(f"Result: {'✅ PASS' if response.status_code == 200 else '❌ FAIL'}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")

    # Test 4: Request without VAPI_SERVER_SECRET configured
    print("\n[TEST 4] Request when VAPI_SERVER_SECRET is not set (should allow)")
    print("-" * 60)
    del os.environ['VAPI_SERVER_SECRET']
    # Need to reload app to test this - simplified for demo
    print("Note: This test requires app reload without VAPI_SECRET env var")
    print("In production: if VAPI_SECRET is not set, webhook is open (for development)")

    print("\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_webhook_security()
