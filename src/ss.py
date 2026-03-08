#!/usr/bin/env python3
"""
Advanced Auto Screenshot CLI
Capture websites (full page, viewport, devices), screen regions, with advanced options
"""

import argparse
import asyncio
import datetime
import io
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image
import pyautogui
from colorama import init, Fore, Style
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import requests
import pyperclip  # untuk clipboard setelah upload

init(autoreset=True)

def cprint(text, color=Fore.WHITE, **kwargs):
    print(color + text + Style.RESET_ALL, **kwargs)

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

            await page.goto(url, wait_until="networkidle", timeout=60000)

            if args.wait_selector:
                try:
                    await page.wait_for_selector(args.wait_selector, timeout=15000)
                except PlaywrightTimeout:
                    cprint("Wait selector not found in time, continuing...", Fore.YELLOW)

            if args.hide_selectors:
                for sel in args.hide_selectors.split(","):
                    sel = sel.strip()
                    await page.evaluate(f"""() => {{
                        document.querySelectorAll('{sel}').forEach(el => el.style.display = 'none');
                    }}""")

            if args.delay > 0:
                await asyncio.sleep(args.delay)

            # FIX: viewport_size adalah property sync (dict), BUKAN async → hilangkan await
            viewport = page.viewport_size  # langsung dict {'width': ..., 'height': ...}

            if args.full_page:
                screenshot_bytes = await page.screenshot(full_page=True, type="png")
            else:
                screenshot_bytes = await page.screenshot(type="png")

            # Buka dari bytes (Playwright handle size internal, tidak perlu manual frombytes lagi)
            img = Image.open(io.BytesIO(screenshot_bytes))

            # Naming
            domain = get_domain_from_url(url)
            filename = f"{domain}_{get_timestamp()}.png" if not args.output else args.output
            output_path = Path(filename)

            save_image(img, output_path)

            if args.upload:
                await upload_to_imgur(output_path, args.upload_key or os.getenv("IMGUR_CLIENT_ID"))

        except Exception as e:
            cprint(f"Error capturing {url}: {str(e)}", Fore.RED)

        finally:
            await browser.close()

async def upload_to_imgur(image_path: Path, client_id=None):
    if not client_id:
        cprint("No Imgur Client-ID provided (set IMGUR_CLIENT_ID env or --upload-key). Skipping upload.", Fore.YELLOW)
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
    parser = argparse.ArgumentParser(description="Advanced Auto Screenshot CLI")
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("--web", type=str, help="URL to screenshot")
    parser.add_argument("--full-page", action="store_true", help="Capture full scrollable page")
    parser.add_argument("--viewport-width", type=int, default=1920)
    parser.add_argument("--viewport-height", type=int, default=1080)
    parser.add_argument("--dark-mode", action="store_true")
    parser.add_argument("--mobile", action="store_true")
    parser.add_argument("--touch", action="store_true")
    parser.add_argument("--high-dpi", action="store_true")
    parser.add_argument("--user-agent", type=str)
    parser.add_argument("--wait-selector", type=str)
    parser.add_argument("--hide", dest="hide_selectors", type=str)
    parser.add_argument("--delay", type=float, default=0)

    group.add_argument("--full-screen", action="store_true")
    group.add_argument("--region", nargs=4, type=int, metavar=("X","Y","W","H"))

    parser.add_argument("--output", type=str)
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--upload-key", type=str)

    args = parser.parse_args()

    if args.web:
        if not args.web.startswith(("http://", "https://")):
            args.web = "https://" + args.web
        await screenshot_web(args.web, args)

    elif args.full_screen:
        output = args.output or f"screenshot_{get_timestamp()}.png"
        screenshot_screen_full(Path(output))

    elif args.region:
        output = args.output or f"screenshot_{get_timestamp()}.png"
        screenshot_region(*args.region, Path(output))

    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
