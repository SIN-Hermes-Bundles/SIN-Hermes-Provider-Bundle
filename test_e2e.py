#!/usr/bin/env python3
"""
E2E-Test fuer SINator-FireworksAI Rotation.
Durchlauft GMX Login -> Alias Rotation -> Fireworks Signup -> OTP -> API Key.
"""
import sys
import os
import asyncio

# Add agent_toolbox to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent_toolbox'))

from core.fireworks_service import browser_login_gmx, rotate_gmx_alias, read_otp_gmx, signup_fireworks, create_api_key_fireworks
from core.gmx_service import get_gmx_service
from core.config_manager import get_config

async def main():
    print("=== SINator E2E Test ===")
    
    config = get_config()
    email = config.gmx_email
    password = config.gmx_password
    fw_password = config.fireworks_password
    
    # Test 1: Browser-Login
    print("\n[1] GMX Browser-Login...")
    try:
        result = await browser_login_gmx(email=email, password=password)
        print(f"  Status: {result.get('status')}")
        print(f"  URL: {result.get('url')}")
        if result.get('error'):
            print(f"  ERROR: {result.get('error')}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test 2: Alias Rotation
    print("\n[2] GMX Alias Rotation...")
    try:
        result = await rotate_gmx_alias()
        print(f"  Status: {result.get('status')}")
        print(f"  Alias: {result.get('alias')}")
        if result.get('error'):
            print(f"  ERROR: {result.get('error')}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test 3: Fireworks Signup
    print("\n[3] Fireworks Signup...")
    alias_email = result.get('alias', email)
    try:
        result = await signup_fireworks(email=alias_email, password=fw_password)
        print(f"  Status: {result.get('status')}")
        print(f"  Email: {result.get('email')}")
        if result.get('error'):
            print(f"  ERROR: {result.get('error')}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test 4: OTP
    print("\n[4] OTP aus GMX lesen...")
    try:
        result = await read_otp_gmx(sender_filter="fireworks")
        print(f"  Status: {result.get('status')}")
        print(f"  OTP: {result.get('otp')}")
        if result.get('error'):
            print(f"  ERROR: {result.get('error')}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test 5: API Key
    print("\n[5] Fireworks API Key erstellen...")
    try:
        result = await create_api_key_fireworks()
        print(f"  Status: {result.get('status')}")
        print(f"  Key: {result.get('api_key')}")
        if result.get('error'):
            print(f"  ERROR: {result.get('error')}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    print("\n=== E2E Test abgeschlossen ===")
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
