#!/usr/bin/env python3
"""
Isolated test for Vapi Webhook Security
Tests only the header verification logic
"""

import os
import sys
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel

# Create minimal test app
app = FastAPI()

# Simulate the VAPI_SERVER_SECRET from env
VAPI_SECRET = os.getenv("VAPI_SERVER_SECRET", "test-secret-123")

@app.post("/vapi/webhook")
async def vapi_webhook(request: Request):
    """Simplified webhook endpoint for testing"""

    # Verify Vapi webhook secret if configured
    if VAPI_SECRET:
        vapi_secret_header = request.headers.get("x-vapi-secret")
        if not vapi_secret_header or vapi_secret_header != VAPI_SECRET:
            raise HTTPException(
                status_code=401,
                detail="Unauthorized: Invalid or missing webhook secret"
            )

    return {"status": "ok", "message": "Webhook received"}

client = TestClient(app)

def run_tests():
    """Run webhook security tests"""

    print("=" * 70)
    print("VAPI WEBHOOK SECURITY TESTS")
    print("=" * 70)
    print(f"VAPI_SERVER_SECRET configured: {'Yes' if VAPI_SECRET else 'No'}")
    print(f"Secret value: {'*' * len(VAPI_SECRET) if VAPI_SECRET else 'N/A'}")
    print()

    test_payload = {
        "message": {"role": "user", "content": "Test message"},
        "call": {"id": "test-123", "customer": {"number": "+49123456789"}}
    }

    tests_passed = 0
    tests_failed = 0

    # Test 1: Request without secret header
    print("TEST 1: Request WITHOUT x-vapi-secret header")
    print("-" * 70)
    response = client.post("/vapi/webhook", json=test_payload)
    status = response.status_code
    expected = 401

    if status == expected:
        print(f"   Status: {status} [PASS]")
        print(f"   Response: {response.json()}")
        tests_passed += 1
    else:
        print(f"   Status: {status} [FAIL] (expected {expected})")
        print(f"   Response: {response.text}")
        tests_failed += 1
    print()

    # Test 2: Request with wrong secret
    print(" TEST 2: Request with WRONG x-vapi-secret header")
    print("-" * 70)
    response = client.post(
        "/vapi/webhook",
        json=test_payload,
        headers={"x-vapi-secret": "wrong-secret-456"}
    )
    status = response.status_code
    expected = 401

    if status == expected:
        print(f"   Status: {status} [PASS]")
        print(f"   Response: {response.json()}")
        tests_passed += 1
    else:
        print(f"   Status: {status} [FAIL] (expected {expected})")
        print(f"   Response: {response.text}")
        tests_failed += 1
    print()

    # Test 3: Request with correct secret
    print(" TEST 3: Request with CORRECT x-vapi-secret header")
    print("-" * 70)
    response = client.post(
        "/vapi/webhook",
        json=test_payload,
        headers={"x-vapi-secret": VAPI_SECRET}
    )
    status = response.status_code
    expected = 200

    if status == expected:
        print(f"   Status: {status} [PASS]")
        print(f"   Response: {response.json()}")
        tests_passed += 1
    else:
        print(f"   Status: {status} [FAIL] (expected {expected})")
        print(f"   Response: {response.text}")
        tests_failed += 1
    print()

    # Test 4: Request with empty secret header
    print(" TEST 4: Request with EMPTY x-vapi-secret header")
    print("-" * 70)
    response = client.post(
        "/vapi/webhook",
        json=test_payload,
        headers={"x-vapi-secret": ""}
    )
    status = response.status_code
    expected = 401

    if status == expected:
        print(f"   Status: {status} [PASS]")
        print(f"   Response: {response.json()}")
        tests_passed += 1
    else:
        print(f"   Status: {status} [FAIL] (expected {expected})")
        print(f"   Response: {response.text}")
        tests_failed += 1
    print()

    # Summary
    print("=" * 70)
    print(" TEST SUMMARY")
    print("=" * 70)
    total = tests_passed + tests_failed
    print(f"   Total Tests: {total}")
    print(f"   Passed: {tests_passed} [PASS]")
    print(f"   Failed: {tests_failed} {'[FAIL]' if tests_failed > 0 else '[PASS]'}")
    print()

    if tests_failed == 0:
        print(" All security tests passed!")
    else:
        print("  Some tests failed - please review the implementation")
    print()

if __name__ == "__main__":
    run_tests()
