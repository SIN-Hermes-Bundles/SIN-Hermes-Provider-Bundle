# Docs: gmx_service.doc.md
"""
SINATOR AGENT-TOOLBOX — GMX Service (Playwright-native v2026-05-28)

Kernfunktionen:
  - GMX Session-Management
  - Alias-Rotation (Löschen + Erstellen)
  - OTP/Confirm-URL Extraktion

Playwright-native für Alias-Rotation. OTP bleibt auf CDP (komplex, funktioniert).
"""
import time
import random
import logging
import re
import asyncio
import json
import html as html_module
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
import httpx

from playwright.async_api import async_playwright, Browser, Page, BrowserContext, Frame

from agent_toolbox.core.cdp_client import (
    CDPClient,
    OopifContext,
    get_browser_ws_endpoint,
    get_page_target,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setLevel(logging.DEBUG)
    _formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    _handler.setFormatter(_formatter)
    logger.addHandler(_handler)

GMX_HOME_URL = "https://www.gmx.net/"


class GmxService:
    def __init__(self):
        self.adjectives = [
            "elron", "dark", "swift", "iron", "silver", "golden", "crystal", "shadow",
            "storm", "frost", "blaze", "thunder", "cosmic", "neon", "cyber", "quantum",
            "alpha", "beta", "delta", "omega", "zenith", "nexus", "vortex", "pulse",
            "echo", "phantom", "spectra", "turbo", "hyper", "ultra", "mega", "super",
        ]
        self.nouns = [
            "vader", "runner", "hawk", "wolf", "fox", "tiger", "eagle", "shark",
            "dragon", "phoenix", "falcon", "panther", "cobra", "lynx", "raven", "jaguar",
            "bear", "lion", "whale", "dolphin", "puma", "cheetah", "otter", "badger",
            "wolverine", "raptor", "condor", "viper", "scorpion", "spider", "mantis", "beetle",
        ]

    def generate_alias_name(self) -> str:
        adj = random.choice(self.adjectives)
        noun = random.choice(self.nouns)
        num = random.randint(100, 999)
        return f"{adj}-{noun}-{num}"

    # ── Playwright Connection ────────────────────────────────────────────

    async def _pw_connect(self, cdp_port: int = 9222) -> Page:
        """Connect to existing Chrome via CDP and return a Playwright Page.
        Prefers allEmailAddresses page if available. Ignores iac/restart pages."""
        logger.info(f"[_pw_connect] Connecting to Chrome on CDP port {cdp_port}")
        p = await async_playwright().start()
        browser = await p.chromium.connect_over_cdp(f"http://localhost:{cdp_port}")
        
        # First, look for allEmailAddresses page
        page = None
        for ctx in browser.contexts:
            for pg in ctx.pages:
                url = pg.url or ""
                if "allEmailAddresses" in url and "settings" in url and "iac/restart" not in url:
                    page = pg
                    logger.info(f"[_pw_connect] Found allEmailAddresses page: {url[:60]}...")
                    return page
        
        # Otherwise, look for any valid GMX page (not iac/restart)
        for ctx in browser.contexts:
            for pg in ctx.pages:
                url = pg.url or ""
                if "gmx.net" in url and "iac/restart" not in url and "session-expired" not in url and "logoutlounge" not in url:
                    page = pg
                    logger.info(f"[_pw_connect] Found GMX page: {url[:60]}...")
                    return page
        
        # Fallback to first page that is not iac/restart
        for ctx in browser.contexts:
            for pg in ctx.pages:
                url = pg.url or ""
                if "iac/restart" not in url and "session-expired" not in url and "logoutlounge" not in url:
                    page = pg
                    logger.info(f"[_pw_connect] Using fallback page: {url[:60]}...")
                    return page
        
        # Last resort: create new page
        if browser.contexts and browser.contexts[0].pages:
            page = browser.contexts[0].pages[0]
            logger.info(f"[_pw_connect] Using first page: {page.url[:60]}...")
        else:
            page = await browser.contexts[0].new_page() if browser.contexts else await browser.new_page()
            logger.info(f"[_pw_connect] Created new page")
        
        return page

    async def _login(self, page: Page, email: str = "delqhi@gmx.de", password: str = "ZOE.jerry2024") -> bool:
        """Login to GMX via Playwright. Two-step flow: Email → Weiter → Password → Login."""
        logger.info(f"[_login] Logging in to GMX as {email}")
        try:
            await page.goto("https://www.gmx.net/", wait_until="domcontentloaded")
            await asyncio.sleep(5)  # Wait for JS redirect
            
            url = page.url
            
            # Handle cookie consent if present
            if "consent" in url:
                logger.info("Cookie consent page detected, accepting")
                try:
                    # Click "Alle akzeptieren" or "Zustimmen" or similar
                    for selector in ['button:has-text("Alle akzeptieren")', 'button:has-text("Zustimmen")', 
                                    'button:has-text("Akzeptieren")', 'button:has-text("OK")',
                                    'button[data-testid="uc-accept-all-button"]']:
                        btn = page.locator(selector).first
                        if await btn.is_visible(timeout=2000):
                            await btn.click()
                            logger.info(f"Clicked consent: {selector}")
                            await asyncio.sleep(3)
                            break
                except Exception as e:
                    logger.warning(f"Consent handling failed: {e}")
                url = page.url
                logger.info(f"After consent: {url[:80]}")
            
            # Already logged in on www.gmx.net homepage with Zum Postfach?
            text = await page.evaluate("() => document.body.innerText")
            if "Sie sind eingeloggt" in text or "Zum Postfach" in text:
                logger.info("Detected logged-in state on homepage, clicking Zum Postfach")
                try:
                    postfach_link = page.locator('text=Zum Postfach').first
                    if await postfach_link.is_visible(timeout=3000):
                        await postfach_link.click()
                        await asyncio.sleep(5)
                        logger.info(f"Postfach URL: {page.url[:80]}")
                        if "navigator.gmx.net/mail?sid=" in page.url:
                            return True
                        if "navigator.gmx.net" in page.url:
                            # Might be bap redirect — extract SID
                            return True
                except Exception as e:
                    logger.warning(f"Zum Postfach click failed: {e}")
                
                # Try direct navigation to inbox
                logger.info("Trying direct navigator.gmx.net/mail")
                await page.goto("https://navigator.gmx.net/mail", wait_until="domcontentloaded")
                await asyncio.sleep(5)
                if "navigator.gmx.net/mail?sid=" in page.url:
                    return True
                if "navigator.gmx.net" in page.url:
                    return True
                
                logger.error("Could not establish GMX session from logged-in homepage")
                return False
            
            # On auth.gmx.net login page — step 1: fill email, click Weiter
            if "auth.gmx.net" in url or "login.gmx.net" in url:
                logger.info("Step 1: Filling email on auth.gmx.net")
                # The email input has name=username, id=email
                email_input = page.locator('input[id="email"], input[name="username"]').first
                if await email_input.is_visible(timeout=5000):
                    await email_input.fill(email)
                    logger.info("Email filled")
                
                # Click Weiter button
                await asyncio.sleep(0.5)
                weiter_btn = page.locator('button:has-text("Weiter")').first
                if await weiter_btn.is_visible(timeout=3000):
                    await weiter_btn.click()
                    logger.info("Clicked Weiter")
                    await asyncio.sleep(4)
                else:
                    # Fallback: find any button with "Weiter"
                    btns = await page.query_selector_all('button')
                    for b in btns:
                        t = (await b.text_content() or '').strip()
                        if 'Weiter' in t:
                            await b.click()
                            logger.info(f"Clicked button: {t}")
                            await asyncio.sleep(4)
                            break
                
                # Step 2: fill password, click Login
                url = page.url
                logger.info(f"After Weiter, URL: {url[:80]}")
                password_input = page.locator('input[type="password"]').first
                if await password_input.is_visible(timeout=5000):
                    await password_input.fill(password)
                    logger.info("Password filled")
                
                await asyncio.sleep(0.5)
                login_btn = page.locator('button:has-text("Login")').first
                if await login_btn.is_visible(timeout=3000):
                    await login_btn.click()
                    logger.info("Clicked Login")
                    await asyncio.sleep(5)
                else:
                    btns = await page.query_selector_all('button')
                    for b in btns:
                        t = (await b.text_content() or '').strip()
                        if 'Login' == t:
                            await b.click()
                            logger.info("Clicked Login button")
                            await asyncio.sleep(5)
                            break
                
                # Check result
                url = page.url
                logger.info(f"After login, URL: {url[:80]}")
                if "navigator.gmx.net/mail?sid=" in url:
                    logger.info("Login successful, got SID")
                    return True
                if "navigator.gmx.net" in url:
                    # Might be on bap, try extracting SID
                    return True
                
                logger.error("Login failed — unexpected URL after login")
                return False
            
            # Fallback: click Login button on homepage first
            logger.info("Homepage without login form — clicking Login button")
            try:
                login_btn = page.locator('button:has-text("Login")').first
                if await login_btn.is_visible(timeout=3000):
                    await login_btn.click()
                    logger.info("Clicked Login button on homepage")
                    await asyncio.sleep(5)
                    url = page.url
                    logger.info(f"After login click: {url[:80]}")
                    
                    # Now we should be on auth.gmx.net — proceed with two-step
                    if "auth.gmx.net" in url or "login.gmx.net" in url:
                        logger.info("On login page after clicking Login")
                        # Fill email (step 1)
                        email_input = page.locator('input[id="email"], input[name="username"]').first
                        if await email_input.is_visible(timeout=5000):
                            await email_input.fill(email)
                            logger.info("Email filled")
                        
                        await asyncio.sleep(0.5)
                        weiter_btn = page.locator('button:has-text("Weiter")').first
                        if await weiter_btn.is_visible(timeout=3000):
                            await weiter_btn.click()
                            logger.info("Clicked Weiter")
                            await asyncio.sleep(4)
                        
                        # Step 2: password
                        password_input = page.locator('input[type="password"]').first
                        if await password_input.is_visible(timeout=5000):
                            await password_input.fill(password)
                            logger.info("Password filled")
                        
                        await asyncio.sleep(0.5)
                        login_btn = page.locator('button:has-text("Login")').first
                        if await login_btn.is_visible(timeout=3000):
                            await login_btn.click()
                            logger.info("Clicked Login")
                            await asyncio.sleep(5)
                        
                        url = page.url
                        logger.info(f"After login: {url[:80]}")
                        if "navigator.gmx.net/mail?sid=" in url:
                            return True
                        if "navigator.gmx.net" in url:
                            return True
                else:
                    logger.warning("Login button not found on homepage")
            except Exception as e:
                logger.warning(f"Homepage login flow failed: {e}")
            
            # Legacy fallback
            logger.info("Trying legacy login flow")
            email_input = page.locator('input[name="email"]').first
            if await email_input.is_visible(timeout=5000):
                await email_input.fill(email)
            password_input = page.locator('input[type="password"]').first
            if await password_input.is_visible(timeout=5000):
                await password_input.fill(password)
            submit_btn = page.locator('button[type="submit"]').first
            if await submit_btn.is_visible(timeout=3000):
                await submit_btn.click()
            await asyncio.sleep(5)
            
            url = page.url
            logger.info(f"Legacy login result URL: {url[:80]}")
            return "navigator.gmx.net" in url
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    # ── Navigation ─────────────────────────────────────────────────────

    async def _navigate_to_all_email_addresses(self, page: Page) -> bool:
        """Navigate to GMX allEmailAddresses via direct 3c.gmx.net jump (v3 approach).
        
        Instead of navigating through the GMX shell (which keeps content in
        cross-origin iframes that break after any action), we use:
          1. Get SID from current session (or login)
          2. Navigate to navigator.gmx.net/navigator/jump/to/mail_settings?sid={sid}
             → redirects to 3c.gmx.net/mail/client/settings/signature/ (TOP FRAME!)
          3. JS dispatchEvent click on "E-Mail-Adressen"
             → navigates to allEmailAddresses (TOP FRAME!)
        
        This keeps all content in the top frame — no iframe fragility.
        """
        url = page.url
        
        # Already on allEmailAddresses in top frame?
        if "allEmailAddresses" in url and "settings" in url:
            logger.info("Already on allEmailAddresses (top frame)")
            return True
        
        # Step 0: Get SID — from current URL, other tabs, or login
        sid = None
        sid_match = re.search(r'[?&]sid=([a-f0-9]{50,})', url)
        if sid_match:
            sid = sid_match.group(1)
        
        if not sid:
            for ctx in page.context.browser.contexts:
                for pg in ctx.pages:
                    m = re.search(r'[?&]sid=([a-f0-9]{50,})', pg.url)
                    if m and "gmx.net" in pg.url:
                        sid = m.group(1)
                        logger.info(f"Got SID from other tab: {pg.url[:60]}")
                        break
                if sid:
                    break
        
        if not sid:
            logger.info("No SID found, logging in")
            if not await self._login(page):
                return False
            sid_match = re.search(r'[?&]sid=([a-f0-9]{50,})', page.url)
            sid = sid_match.group(1) if sid_match else None
        
        if not sid:
            logger.error("Could not establish GMX session")
            return False
        
        logger.info(f"Got SID: {sid[:20]}...")
        
        # Step 1: Navigate to jump URL → redirects to 3c.gmx.net (top frame!)
        jump_url = f"https://navigator.gmx.net/navigator/jump/to/mail_settings?sid={sid}"
        logger.info(f"STEP 1: Navigating to jump URL")
        await page.goto(jump_url, wait_until="domcontentloaded")
        await asyncio.sleep(6)
        
        url = page.url
        logger.info(f"After jump: {url[:100]}")
        
        if "allEmailAddresses" in url:
            logger.info("Redirected directly to allEmailAddresses (top frame)")
            return True
        
        # Step 2: On settings/signature → click "E-Mail-Adressen"
        if "settings" in url and "3c.gmx.net" in url:
            logger.info("STEP 2: On 3c.gmx.net settings — clicking E-Mail-Adressen via JS")
            try:
                result = await page.evaluate("""(function() {
                    var allEls = document.querySelectorAll('a, span, li, div, p');
                    for (var i = 0; i < allEls.length; i++) {
                        var el = allEls[i];
                        if (el.children.length === 0 && el.textContent.trim() === 'E-Mail-Adressen') {
                            var rect = el.getBoundingClientRect();
                            var cx = rect.x + rect.width / 2;
                            var cy = rect.y + rect.height / 2;
                            ['mousedown', 'mouseup', 'click'].forEach(function(evtType) {
                                el.dispatchEvent(new MouseEvent(evtType, {
                                    bubbles: true, cancelable: true, view: window,
                                    clientX: cx, clientY: cy
                                }));
                            });
                            return {clicked: true};
                        }
                    }
                    return {clicked: false};
                })()""")
                if result.get("clicked"):
                    logger.info("E-Mail-Adressen clicked via JS dispatchEvent")
                    await asyncio.sleep(4)
                else:
                    logger.warning("E-Mail-Adressen element not found on settings page")
            except Exception as e:
                logger.warning(f"E-Mail-Adressen JS click failed: {e}")
        
        # Step 3: Verify we're on allEmailAddresses
        url = page.url
        logger.info(f"Final URL: {url[:100]}")
        if "allEmailAddresses" in url and "settings" in url:
            logger.info("Successfully navigated to allEmailAddresses (top frame)")
            return True
        
        # Fallback: poll for allEmailAddresses frame
        logger.info("STEP 3: Polling for allEmailAddresses")
        for poll in range(15):
            if "allEmailAddresses" in page.url and "settings" in page.url:
                return True
            await asyncio.sleep(1)
        
        logger.error("allEmailAddresses not found")
        return False

    # ── Alias Deletion ──────────────────────────────────────────────────

    async def _get_all_email_frame(self, page: Page) -> Optional[Frame]:
        """Find the allEmailAddresses iframe, or return main_frame if in top frame."""
        # If page itself is on allEmailAddresses (jump approach), use main frame
        if "allEmailAddresses" in page.url and "settings" in page.url:
            return page.main_frame
        # Fallback: search frames
        for frame in page.frames:
            if "allEmailAddresses" in frame.url and "settings" in frame.url and "iac/restart" not in frame.url:
                return frame
        return None

    async def _find_alias_row(self, page: Page) -> Optional[str]:
        """Find a non-opensin alias email in the allEmailAddresses iframe."""
        logger.info("[_find_alias_row] Searching for alias")
        try:
            frame = await self._get_all_email_frame(page)
            if not frame:
                logger.warning("allEmailAddresses iframe not found")
                return None
            
            text = await frame.evaluate("() => document.body.innerText")
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if '@gmx.' in line and 'delqhi@gmx.de' not in line and 'opensin@gmx.de' not in line:
                    parts = line.split()
                    for part in parts:
                        if '@gmx.' in part and part != 'delqhi@gmx.de' and part != 'opensin@gmx.de':
                            logger.info(f"Found alias: {part}")
                            return part
        except Exception as e:
            logger.warning(f"Error finding alias: {e}")
        return None

    async def _delete_alias(self, page: Page, alias_email: str) -> bool:
        """Delete an alias by hovering over its row and clicking delete."""
        logger.info(f"[_delete_alias] Deleting {alias_email}")
        try:
            frame = await self._get_all_email_frame(page)
            if not frame:
                logger.warning("allEmailAddresses iframe not found for delete")
                return False
            
            # Find the row containing the alias email
            row = frame.locator(f'text={alias_email}').first
            if not await row.is_visible(timeout=3000):
                logger.warning(f"Alias row not visible: {alias_email}")
                return False

            # Hover to reveal delete button
            await row.hover()
            await asyncio.sleep(1)

            # Look for delete button (title or aria-label containing "lösch")
            delete_btn = frame.locator('[title*="lösch" i], [aria-label*="lösch" i]').first
            if not await delete_btn.is_visible(timeout=2000):
                # Try any button near the alias
                delete_btn = frame.locator('button').filter(has=frame.locator('svg, i, img')).first

            if await delete_btn.is_visible(timeout=2000):
                logger.info("Clicking delete button")
                await delete_btn.click(force=True)
                await asyncio.sleep(3)

                # Confirm dialog
                try:
                    ok_btn = frame.locator('button:has-text("OK")').first
                    if await ok_btn.is_visible(timeout=2000):
                        await ok_btn.click()
                        await asyncio.sleep(2)
                except:
                    pass

                # Verify deletion
                for _ in range(10):
                    text = await frame.evaluate("() => document.body.innerText")
                    if alias_email not in text:
                        logger.info("Alias deleted successfully")
                        return True
                    await asyncio.sleep(1)

            logger.warning("Delete button not found")
            return False
        except Exception as e:
            logger.error(f"Error deleting alias: {e}")
            return False

    # ── Alias Creation ──────────────────────────────────────────────────

    async def _fill_alias_input(self, page: Page, alias_name: str) -> bool:
        """Fill the alias input field in the allEmailAddresses iframe."""
        logger.info(f"[_fill_alias_input] Filling with {alias_name}")
        try:
            frame = await self._get_all_email_frame(page)
            if not frame:
                logger.warning("allEmailAddresses iframe not found")
                return False
            
            # Try input[name*="localPart"]
            inp = frame.locator('input[name*="localPart"]').first
            if not await inp.is_visible(timeout=3000):
                # Try any text input
                inp = frame.locator('input[type="text"]').first

            if await inp.is_visible(timeout=3000):
                await inp.fill(alias_name)
                # Trigger events for React
                await inp.evaluate("el => el.dispatchEvent(new Event('input', {bubbles: true, composed: true}))")
                await inp.evaluate("el => el.dispatchEvent(new Event('change', {bubbles: true}))")
                value = await inp.input_value()
                if value == alias_name:
                    logger.info("Alias input filled successfully")
                    return True
            logger.warning("Alias input not found")
            return False
        except Exception as e:
            logger.error(f"Error filling alias input: {e}")
            return False

    async def _click_add_button(self, page: Page) -> bool:
        """Click the add alias button. No reload — let page handle navigation internally."""
        logger.info("[_click_add_button] Looking for add button")
        try:
            frame = await self._get_all_email_frame(page)
            if not frame:
                logger.warning("allEmailAddresses iframe not found")
                return False
            
            # Click via JS evaluate (most reliable with Wicket)
            result = await frame.evaluate("""(function() {
                var btns = document.querySelectorAll('button');
                for (var i = 0; i < btns.length; i++) {
                    if (btns[i].textContent.indexOf('Hinzuf') >= 0) {
                        btns[i].click();
                        return true;
                    }
                }
                return false;
            })()""")
            if result:
                logger.info("Hinzufügen button clicked via JS")
                await asyncio.sleep(2)
                return True
            
            logger.warning("Add button not found")
            return False
        except Exception as e:
            logger.error(f"Error clicking add button: {e}")
            return False

    async def _verify_alias(self, page: Page, alias_email: str, present: bool = True, max_wait: float = 12.0) -> bool:
        """Verify alias is present/absent in the allEmailAddresses page."""
        logger.info(f"[_verify_alias] Checking {alias_email} present={present}")
        try:
            deadline = time.time() + max_wait
            while time.time() < deadline:
                # Check page URL first (top frame approach)
                if "allEmailAddresses" in page.url and "settings" in page.url:
                    text = await page.evaluate("() => document.body.innerText")
                    found = alias_email in text
                    if present and found:
                        return True
                    if not present and not found:
                        return True
                else:
                    # Search across all frames (fallback)
                    for frame in page.frames:
                        if "allEmailAddresses" in frame.url and "settings" in frame.url:
                            text = await frame.evaluate("() => document.body.innerText")
                            found = alias_email in text
                            if present and found:
                                return True
                            if not present and not found:
                                return True
                            break
                await asyncio.sleep(1)
            return False
        except Exception as e:
            logger.error(f"Error verifying alias: {e}")
            return False

    async def create_alias(self, alias_name: Optional[str] = None, cdp_port: int = 9222) -> Dict[str, Any]:
        if not alias_name:
            alias_name = self.generate_alias_name()
        try:
            page = await self._pw_connect(cdp_port)
            if not await self._navigate_to_all_email_addresses(page):
                return {"status": "not_logged_in", "alias_email": None, "error": "Navigation fehlgeschlagen"}

            for attempt in range(3):
                current_alias = alias_name if attempt == 0 else self.generate_alias_name()
                alias_email = f"{current_alias}@gmx.de"
                logger.info(f"Erstelle Alias (Versuch {attempt+1}/3): {alias_email}")

                if not await self._fill_alias_input(page, current_alias):
                    return {"status": "error", "alias_email": None, "error": "Input-Fill fehlgeschlagen"}
                await asyncio.sleep(1)

                if not await self._click_add_button(page):
                    return {"status": "error", "alias_email": None, "error": "Hinzufügen-Button nicht gefunden"}
                await asyncio.sleep(3)

                if await self._verify_alias(page, alias_email, present=True):
                    return {"status": "success", "alias_email": alias_email}
                await asyncio.sleep(1)

            return {"status": "failed", "alias_email": None, "error": "Alle Versuche fehlgeschlagen"}
        except Exception as e:
            logger.error(f"Alias-Erstellung fehlgeschlagen: {e}")
            return {"status": "error", "alias_email": None, "error": str(e)}

    # ── Alias Rotation ────────────────────────────────────────────────────

    async def rotate_alias(self, new_alias_name: Optional[str] = None, cdp_port: int = 9222) -> Dict[str, Any]:
        start_time = time.time()
        steps = []
        deleted_alias = None
        created_alias = None
        try:
            page = await self._pw_connect(cdp_port)
            if not await self._navigate_to_all_email_addresses(page):
                return {"status": "failed", "deleted_alias": None, "created_alias": None,
                        "error": "Navigation fehlgeschlagen", "execution_time": f"{time.time()-start_time:.2f}s"}
            steps.append("navigated")

            # Try to delete existing alias
            alias_email = await self._find_alias_row(page)
            if alias_email:
                logger.info(f"Found alias to delete: {alias_email}")
                if await self._delete_alias(page, alias_email):
                    deleted_alias = alias_email
                    steps.append("deleted")
                    # Don't reload — it breaks session. Just wait for DOM to settle.
                    await asyncio.sleep(3)
                else:
                    logger.warning("Failed to delete alias, continuing")
            else:
                steps.append("no_alias_to_delete")

            # Create new alias
            if not new_alias_name:
                new_alias_name = self.generate_alias_name()
            for attempt in range(3):
                current_alias = new_alias_name if attempt == 0 else self.generate_alias_name()
                alias_email = f"{current_alias}@gmx.de"
                logger.info(f"Creating alias (attempt {attempt+1}/3): {alias_email}")

                if await self._fill_alias_input(page, current_alias):
                    await asyncio.sleep(1)
                    if await self._click_add_button(page):
                        await asyncio.sleep(3)
                        if await self._verify_alias(page, alias_email, present=True):
                            created_alias = alias_email
                            steps.append("created")
                            break
                await asyncio.sleep(1)

            if created_alias:
                return {"status": "success", "deleted_alias": deleted_alias, "created_alias": created_alias,
                        "steps": steps, "execution_time": f"{time.time()-start_time:.2f}s"}
            return {"status": "failed", "deleted_alias": deleted_alias, "created_alias": None,
                    "error": "Erstellung fehlgeschlagen", "steps": steps, "execution_time": f"{time.time()-start_time:.2f}s"}
        except Exception as e:
            logger.error(f"Rotation fehlgeschlagen: {e}")
            return {"status": "failed", "error": str(e), "steps": steps, "execution_time": f"{time.time()-start_time:.2f}s"}

    # ── OTP / Confirm URL ───────────────────────────────────────────────────
    # OTP bleibt auf CDP — funktioniert, komplex (MailCheck Extension, OOPIF)

    async def _cdp_extract_url_from_email_body(self, cdp_port: int) -> Optional[str]:
        """After clicking the email, extract Fireworks verify URL from the email body.
        
        The opened email loads in an OOPIF from gmxnet.mailbody-ui.de.
        Find that iframe target, attach to it, and extract the URL from its content.
        """
        try:
            ws_url = await get_browser_ws_endpoint(cdp_port)
            cdp = CDPClient(ws_url)
            await cdp.connect()
            try:
                # Try mailbody-ui.de OOPIF — attach directly by target type + url
                attached = await cdp.attach_to_iframe("mailbody-ui.de")
                if attached:
                    child_sid, target = attached
                    text = await cdp.evaluate(child_sid, "document.body.innerText")
                    body = text.get("result", {}).get("value", "")
                    if body:
                        urls = re.findall(r'https://app\.fireworks\.ai/[^\s"\'<>]+', body)
                        candidates = [u for u in urls if any(
                            k in u.lower() for k in ["confirm", "verify", "token", "auth", "activate", "signup"])]
                        if candidates:
                            return html_module.unescape(candidates[0])
                
                # Fallback: search all navigator.gmx.net pages for fireworks URL
                targets = await cdp.get_targets()
                for t in targets:
                    url = t.get("url", "")
                    if t.get("type") == "page" and ("navigator.gmx.net" in url or "mailbody" in url):
                        sid = await cdp.attach_to_target(t["targetId"])
                        text = await cdp.evaluate(sid, "document.body.innerText")
                        result = text.get("result", {}).get("value", "")
                        urls = re.findall(r'https://app\.fireworks\.ai/[^\s"\'<>]+', str(result))
                        candidates = [u for u in urls if any(
                            k in u.lower() for k in ["confirm", "verify", "token", "auth", "activate", "signup"])]
                        if candidates:
                            return html_module.unescape(candidates[0])
                return None
            finally:
                await cdp.disconnect()
        except Exception as e:
            logger.debug(f"CDP URL extraction failed: {e}")
            return None

    async def _ensure_gmx_inbox(self, page: Page, cdp_port: int = 9222) -> bool:
        """Zur GMX Inbox navigieren OHNE page.goto (killt Session).
        
        Nutzt CDP Target Discovery + SPA-Klicks. Nie page.goto/reload auf GMX.
        """
        url = page.url
        if "navigator.gmx.net" in url and "mail?sid=" in url:
            return True
        if "bap.navigator.gmx.net" in url and "mail?sid=" in url:
            return True
        
        logger.info(f"Current page: {url[:80]} — searching for inbox...")
        
        # 1. CDP: finde existierende GMX inbox page
        ws_url = await get_browser_ws_endpoint(cdp_port)
        cdp = CDPClient(ws_url)
        await cdp.connect()
        try:
            targets = await cdp.get_targets()
            inbox_pages = [t for t in targets if t.get("type") == "page"
                          and ("navigator.gmx.net" in t.get("url", "") or "bap.navigator.gmx.net" in t.get("url", ""))
                          and "mail?sid=" in t.get("url", "")]
            if inbox_pages:
                logger.info(f"Found inbox in another tab: {inbox_pages[0]['url'][:60]}...")
                return True
        finally:
            await cdp.disconnect()
        
        # 2. SPA-Navigation via Klicks (nur auf GMX-Seiten)
        if "gmx.net" in url or "gmx.de" in url:
            for _ in range(5):
                try:
                    await page.locator('a:has-text("E-Mail")').first.click(timeout=3000)
                    await asyncio.sleep(5)
                    if "navigator.gmx.net" in page.url or "bap.navigator.gmx.net" in page.url:
                        return True if "mail?sid=" in page.url else True
                except Exception:
                    await asyncio.sleep(2)
            
            # Versuche "Postfach" oder "Inbox"
            for label in ["Postfach", "Inbox", "Mail"]:
                try:
                    btn = page.locator(f'text={label}').first
                    if await btn.is_visible(timeout=2000):
                        await btn.click()
                        await asyncio.sleep(4)
                        return True
                except Exception:
                    continue
        
        logger.warning("Could not reach GMX inbox via SPA clicks")
        return False

    async def read_otp(self, sender_filter: str = "fireworks", max_retries: int = 25, retry_delay: int = 8, cdp_port: int = 9222) -> Dict[str, Any]:
        start_time = time.time()
        try:
            page = await self._pw_connect(cdp_port)
            
            # Einmalig zur GMX Inbox navigieren — danach KEIN page.reload/page.goto mehr!
            if not await self._ensure_gmx_inbox(page, cdp_port):
                return {"status": "not_logged_in", "otp_url": None, "error": "Konnte nicht zur GMX Inbox navigieren"}
            
            logger.info(f"Inbox URL: {page.url[:80]}")
            
            # CDP Client für webmailer iframe + Shadow DOM
            ws_url = await get_browser_ws_endpoint(cdp_port)
            
            # Poll for email (via CDP im webmailer iframe)
            for attempt in range(max_retries):
                logger.info(f"OTP search attempt {attempt+1}/{max_retries}")
                
                # Connect CDP and attach to webmailer iframe
                cdp = CDPClient(ws_url)
                await cdp.connect()
                try:
                    # Attach to webmailer iframe (cross-origin, CDP hat keine CORS Limits)
                    attached = await cdp.attach_to_iframe("webmailer.gmx.net")
                    if attached:
                        wm_sid, wm_target = attached
                        # Enable runtime for JS evaluation
                        try: await cdp.send_to_session(wm_sid, "Runtime.enable")
                        except: pass
                        
                        # Search + click via JS evaluate in webmailer context
                        result = await cdp.evaluate(wm_sid, f"""(function() {{
                            const query = '{sender_filter}'.toLowerCase();
                            function walk(root, depth) {{
                                if (depth > 5) return null;
                                if (!root || typeof root.querySelectorAll !== 'function') return null;
                                const all = root.querySelectorAll('*');
                                for (let i = 0; i < all.length; i++) {{
                                    const el = all[i];
                                    const text = (el.textContent || '').toLowerCase();
                                    if (text.includes(query)) {{
                                        let target = el;
                                        for (let j = 0; j < 5; j++) {{
                                            if (!target) break;
                                            const tag = (target.tagName || '').toLowerCase();
                                            const role = (target.getAttribute('role') || '').toLowerCase();
                                            if (tag === 'list-mail-item' || role === 'row' || role === 'link') {{
                                                target.click();
                                                return {{clicked: true, tag: tag}};
                                            }}
                                            target = target.parentElement;
                                        }}
                                        try {{ el.click(); return {{clicked: true, method: 'direct'}}; }} catch(e) {{}}
                                    }}
                                    if (el.shadowRoot) {{
                                        const found = walk(el.shadowRoot, depth + 1);
                                        if (found && found.clicked) return found;
                                    }}
                                }}
                                return null;
                            }}
                            return walk(document, 0);
                        }})()""")
                        
                        clicked = result and result.get("result", {}).get("value", {}).get("clicked")
                        
                        if clicked:
                            logger.info("Clicked email in webmailer via CDP")
                            await asyncio.sleep(5)
                            
                            # Extract URL from webmailer
                            text_result = await cdp.evaluate(wm_sid, "document.body.innerText")
                            body_text = text_result.get("result", {}).get("value", "")
                            urls = re.findall(r'https://app\.fireworks\.ai/[^\s"\'<>]+', body_text)
                            candidates = [u for u in urls if any(
                                k in u.lower() for k in ["confirm", "verify", "token", "auth", "activate", "signup"])]
                            if candidates:
                                confirm_url = html_module.unescape(candidates[0])
                                logger.info(f"OTP URL found via webmailer: {confirm_url[:80]}...")
                                return {{
                                    "status": "success",
                                    "otp_url": confirm_url,
                                    "execution_time": f"{time.time()-start_time:.2f}s"
                                }}
                    else:
                        logger.info("webmailer iframe not yet found, retrying...")
                except Exception as e:
                    logger.debug(f"Webmailer CDP attempt failed: {e}")
                finally:
                    await cdp.disconnect()
                
                # Also try CDP mailbody extraction (for already-opened emails)
                confirm_url = await self._cdp_extract_url_from_email_body(cdp_port)
                if confirm_url:
                    logger.info(f"OTP URL found via OOPIF: {confirm_url[:80]}...")
                    return {
                        "status": "success",
                        "otp_url": confirm_url,
                        "execution_time": f"{time.time()-start_time:.2f}s"
                    }
                
                if attempt < max_retries - 1:
                    logger.info(f"No URL yet, waiting {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
            
            logger.warning("OTP email not found after all attempts")
            return {"status": "not_found", "otp_url": None, "error": "Nicht gefunden"}
            
        except Exception as e:
            logger.error(f"OTP search failed: {e}")
            return {"status": "error", "otp_url": None, "error": str(e)}

    async def check_session(self, cdp_port: int = 9222) -> Dict[str, Any]:
        """Check GMX session WITHOUT page.goto (killt Session).
        Nutzt CDP Targets um existierende GMX-Pages zu finden + DOM zu checken.
        """
        try:
            ws_url = await get_browser_ws_endpoint(cdp_port)
            cdp = CDPClient(ws_url)
            await cdp.connect()
            try:
                targets = await cdp.get_targets()
                gmx_pages = [t for t in targets if t.get("type") == "page"
                             and ("gmx.net" in t.get("url", "") or "gmx.de" in t.get("url", ""))]
                if not gmx_pages:
                    return {"status": "not_logged_in", "current_url": "", "note": "no gmx page found"}

                for t in gmx_pages:
                    sid = await cdp.attach_to_target(t["targetId"])
                    try:
                        await cdp.send_to_session(sid, "Runtime.enable")
                    except Exception:
                        pass
                    result = await cdp.evaluate(sid, "document.body.innerText")
                    text = result.get("result", {}).get("value", "")
                    if "Sie sind eingeloggt" in text or "Zum Postfach" in text:
                        return {"status": "logged_in", "current_url": t["url"]}
                return {"status": "not_logged_in", "current_url": gmx_pages[0]["url"]}
            finally:
                await cdp.disconnect()
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def open_email_addresses(self, cdp_port: int = 9222) -> Dict[str, Any]:
        try:
            page = await self._pw_connect(cdp_port)
            ok = await self._navigate_to_all_email_addresses(page)
            return {"status": "success" if ok else "error", "current_url": page.url}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # (Legacy Cookie Injection removed — CDP Session Recovery via attach_to_iframe)


_gmx_service: Optional[GmxService] = None


def get_gmx_service() -> GmxService:
    global _gmx_service
    if _gmx_service is None:
        _gmx_service = GmxService()
    return _gmx_service
