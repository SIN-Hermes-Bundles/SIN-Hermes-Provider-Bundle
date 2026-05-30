#!/usr/bin/env python3
"""
GMX Email Opener — CLI Tool

Öffnet eine Email im GMX Webmailer per Shadow DOM Walk.
Findet die Email anhand des Sender-Filters und klickt sie.
Kein OTP, keine URL-Extraktion — nur Öffnen.

Usage:
    python tools/open_gmx_email.py --sender fireworks
    python tools/open_gmx_email.py --sender "no-reply@fireworks.ai"
    python tools/open_gmx_email.py --sender "verify" --port 9222
"""
import asyncio
import json
import sys
import os
import argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agent_toolbox', 'core'))
from gmx_service import GmxService


async def main():
    parser = argparse.ArgumentParser(description="GMX Email Opener")
    parser.add_argument("--sender", default="fireworks", help="Sender-Filter (Text in Email)")
    parser.add_argument("--port", type=int, default=9222, help="CDP Port")
    args = parser.parse_args()

    gmx = GmxService()
    result = await gmx.open_gmx_email(
        sender_filter=args.sender,
        cdp_port=args.port
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
