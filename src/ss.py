#!/usr/bin/env python3
"""
Advanced Auto Screenshot CLI
Capture websites (full page, viewport, devices), screen regions, windows, Android (ADB), with advanced options
"""

import argparse
import asyncio
import datetime
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image
import pyautogui
from colorama import init, Fore, Style
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from tqdm import tqdm
import requests

init(autoreset=True)

COLOR = True  # colorama aktif

def cprint(text, color=Fore.WHITE, **kwargs):
    if COLOR:
        print(color + text + Style.RESET_ALL, **kwargs)
    else:
        print(text, **kwargs)

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def get_domain_from_url(url):
    try:
        return urlparse(url).netloc.replace(".", "_")
    except:
        return "unknown_domain"

def save_image(img_data, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img_data.save(output_path, optimize=True)
    cprint(f"Saved: {output_path}", Fore.GREEN)

async def screenshot_web(url: str, args):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': args.viewport_width, 'height': args.viewport_height} if args.viewport_width else None,
            user_agent=args.user_agent,
            device_scale_factor=2 if args.high_dpi else 1,
            is_mobile=args.mobile,
            has_touch=args.touch,
            locale="en-US",
            timezone_id="Asia/Singapore",
            color_scheme="dark" if args.dark_mode else "light",
        )

        page = await context.new_page()

        try:
            cprint(f"Loading {url} ...", Fore.CYAN)

            # Navigate
            await page.goto(url, wait_until="networkidle", timeout=60000)

            # Wait for selector if specified
            if args.wait_selector:
                try:
                    await page.wait_for_selector(args.wait_selector, timeout=15000)
                except PlaywrightTimeout:
                    cprint("Wait selector not found in time, continuing...", Fore.YELLOW)

            # Hide elements
            if args.hide_selectors:
                for sel in args.hide_selectors.split(","):
                    sel = sel.strip()
                    await page.evaluate(f"""() => {{
                        document.querySelectorAll('{sel}').forEach(el => el.style.display = 'none');
                    }}""")

            # Delay extra if needed
            if args.delay > 0:
                await asyncio.sleep(args.delay)

            # Capture
            if args.full_page:
                screenshot_bytes = await page.screenshot(full_page=True, type="png")
            else:
                screenshot_bytes = await page.screenshot(type="png")

            img = Image.frombytes("RGBA", (await page.viewport_size.values()), screenshot_bytes) if args.full_page else Image.open(io.BytesIO(screenshot_bytes))

            # Naming
            domain = get_domain_from_url(url)
            filename = f"{domain}_{get_timestamp()}.png" if not args.output else args.output
            output_path = Path(filename)

            save_image(img, output_path)

            # Upload if requested
            if args.upload:
                await upload_to_imgur(output_path, args.upload_key)

        except Exception as e:
            cprint(f"Error capturing {url}: {str(e)}", Fore.RED)

        finally:
            await browser.close()

async def upload_to_imgur(image_path: Path, client_id=None):
    if not client_id:
        cprint("No Imgur Client-ID provided. Skipping upload.", Fore.YELLOW)
        return

    try:
        url = "https://api.imgur.com/3/image"
        headers = {"Authorization": f"Client-ID {client_id}"}
        with open(image_path, "rb") as f:
            files = {"image": f}
            response = requests.post(url, headers=headers, files=files)
            if response.status_code == 200:
                data = response.json()
                link = data["data"]["link"]
                cprint(f"Uploaded to Imgur: {link}", Fore.GREEN)
                pyperclip.copy(link)
                cprint("Link copied to clipboard!", Fore.GREEN)
            else:
                cprint(f"Upload failed: {response.text}", Fore.RED)
    except Exception as e:
        cprint(f"Imgur upload error: {e}", Fore.RED)

def screenshot_screen_full(output_path):
    img = pyautogui.screenshot()
    img.save(output_path)
    cprint(f"Full screen saved: {output_path}", Fore.GREEN)

def screenshot_region(x, y, w, h, output_path):
    img = pyautogui.screenshot(region=(x, y, w, h))
    img.save(output_path)
    cprint(f"Region saved: {output_path}", Fore.GREEN)

async def main():
    parser = argparse.ArgumentParser(description="Advanced Auto Screenshot CLI - Web, Screen, Region")
    group = parser.add_mutually_exclusive_group(required=True)

    # Web capture
    group.add_argument("--web", type=str, help="URL to screenshot")
    parser.add_argument("--full-page", action="store_true", help="Capture full scrollable page")
    parser.add_argument("--viewport-width", type=int, default=1920, help="Viewport width")
    parser.add_argument("--viewport-height", type=int, default=1080, help="Viewport height")
    parser.add_argument("--dark-mode", action="store_true", help="Force dark theme")
    parser.add_argument("--mobile", action="store_true", help="Emulate mobile device")
    parser.add_argument("--touch", action="store_true", help="Enable touch emulation")
    parser.add_argument("--high-dpi", action="store_true", help="2x scale for retina")
    parser.add_argument("--user-agent", type=str, help="Custom User-Agent")
    parser.add_argument("--wait-selector", type=str, help="Wait for this CSS selector")
    parser.add_argument("--hide", dest="hide_selectors", type=str, help="Hide CSS selectors (comma separated)")
    parser.add_argument("--delay", type=float, default=0, help="Extra delay after load (seconds)")

    # Screen / Region
    group.add_argument("--full-screen", action="store_true", help="Capture entire screen")
    group.add_argument("--region", nargs=4, type=int, metavar=("X","Y","W","H"), help="Capture region x y width height")

    # Common options
    parser.add_argument("--output", type=str, help="Output file path (default: auto timestamp)")
    parser.add_argument("--upload", action="store_true", help="Upload to Imgur (set IMGUR_CLIENT_ID env var)")
    parser.add_argument("--upload-key", type=str, help="Imgur Client-ID (override env)")

    args = parser.parse_args()

    output = args.output or f"screenshot_{get_timestamp()}.png"
    output_path = Path(output)

    if args.web:
        if not args.web.startswith(("http://", "https://")):
            args.web = "https://" + args.web
        await screenshot_web(args.web, args)

    elif args.full_screen:
        screenshot_screen_full(output_path)

    elif args.region:
        screenshot_region(*args.region, output_path)

    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
