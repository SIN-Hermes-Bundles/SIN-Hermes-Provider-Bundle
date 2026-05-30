#!/usr/bin/env python3
# Docs: rotate.doc.md
"""
SINator - Rotation Tool V8 (2026-05-30)

ONE Playwright browser für den gesamten Prozess.
Kein close/open zwischen GMX und Fireworks mehr.
"""
import sys
import os
import asyncio
import time
import logging
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "agent_toolbox" / "core"))

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("rotate")


async def main():
    parser = argparse.ArgumentParser(description="GMX + Fireworks Rotation")
    parser.add_argument("alias", nargs="?", help="Optional alias name")
    parser.add_argument("--gmx-email", default="delqhi@gmx.de", help="GMX account email")
    parser.add_argument("--gmx-password", default="ZOE.jerry2024", help="GMX account password")
    parser.add_argument("--password", default="ZOE.jerry2024!", help="Fireworks account password")
    parser.add_argument("--save", action="store_true", default=True, help="Save API key to pool")
    parser.add_argument("--cdp-port", type=int, default=9222, help="CDP port for Chrome")
    args = parser.parse_args()

    t0 = time.time()
    from playwright.async_api import async_playwright
    from gmx_service import GmxService
    from fireworks_service import signup_fireworks, login_fireworks, create_api_key, verify_account

    gmx = GmxService()

    # ═══ ONE Browser für den gesamten Prozess ═══
    logger.info("=== Starting shared Playwright browser ===")
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=False)
    page = await browser.new_page()

    try:
        # ═══ Step 1: GMX Alias Rotation ═══
        logger.info("=== GMX Alias Rotation ===")
        result = await gmx.rotate_alias(new_alias_name=args.alias, page=page)
        if result.get('status') != 'success':
            logger.error(f"❌ GMX rotation failed: {result.get('error')}")
            return
        alias = result.get('created_alias')
        logger.info(f"✅ GMX Alias: {alias} ({result.get('execution_time')})")

        # ═══ Step 2: Fireworks Signup (gleicher Browser) ═══
        logger.info("=== Fireworks Signup ===")
        signup_result = await signup_fireworks(alias, args.password, page=page, playwright=p, browser=browser)
        if signup_result.get('status') != 'success':
            logger.error(f"❌ Signup failed: {signup_result.get('error')}")
            return
        logger.info("✅ Signup form submitted, waiting for verification email...")

        # ═══ Step 3: OTP lesen (zurück zu GMX im selben Browser) ═══
        logger.info("=== OTP ===")
        # Navigate back to GMX (shared browser keeps cookies)
        await page.goto("https://www.gmx.net/", timeout=15000)
        await asyncio.sleep(2)
        otp_result = await gmx.read_otp(page=page)
        verify_url = otp_result.get("otp_url")
        if not verify_url:
            logger.error(f"❌ OTP not found: {otp_result.get('error')}")
            return
        logger.info(f"✅ OTP URL: {verify_url[:60]}...")

        # ═══ Step 4: Verify Account (selber Browser) ═══
        await page.goto(verify_url, timeout=20000)
        await asyncio.sleep(3)
        logger.info("✅ Account verified")

        # ═══ Step 5: Fireworks Login + Onboarding (selber Browser) ═══
        logger.info("=== Fireworks Login + Onboarding ===")
        login_result = await login_fireworks(alias, args.password, page=page, playwright=p, browser=browser)
        if login_result.get('status') != 'success':
            logger.error(f"❌ Login failed: {login_result.get('error')}")
            return
        logger.info(f"✅ Login OK")

        # ═══ Step 6: API Key (selber Browser) ═══
        logger.info("=== API Key ===")
        key_name = alias.split("@")[0].split("-")[0] if alias else "sinator-key"
        api_result = await create_api_key(key_name=key_name, page=page, playwright=p, browser=browser)
        api_key = api_result.get("api_key")

        if not api_key:
            logger.error(f"❌ API Key creation failed: {api_result.get('error')}")
            return

        logger.info(f"✅ API Key: {api_key}")

        # ═══ Step 7: Save to pool ═══
        if args.save:
            try:
                from pool_manager import PoolManager
                pool = PoolManager()
                pool.add_key(api_key=api_key, alias_email=alias, key_name=key_name)
                logger.info(f"✅ Saved to pool ({pool.get_stats()['total']} keys total)")
            except Exception as e:
                logger.warning(f"Pool save skipped: {e}")

        elapsed = time.time() - t0
        logger.info(f"\n🎉 ROTATION COMPLETE — {elapsed:.1f}s")
        logger.info(f"   Alias:   {alias}")
        logger.info(f"   API Key: {api_key}")
    finally:
        # ═══ Browser schließen ═══
        try: await browser.close()
        except: pass
        try: await p.stop()
        except: pass
        logger.info("Browser closed")


if __name__ == "__main__":
    asyncio.run(main())
