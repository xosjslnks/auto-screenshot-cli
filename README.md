<p align="center">
  <img src="https://raw.githubusercontent.com/xosjslnks/auto-screenshot-cli/main/assets/logo.png" width="160">
</p>

<h1 align="center">Auto Screenshot CLI</h1>

<p align="center">
Advanced automation tool for capturing clean screenshots from websites, desktops, and devices.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-green">
  <img src="https://img.shields.io/badge/License-MIT-yellow">
  <img src="https://img.shields.io/github/stars/xosjslnks/auto-screenshot-cli?style=social">
</p>

---

# 📸 Auto Screenshot CLI

**Auto Screenshot CLI** adalah tool command-line powerful untuk mengambil screenshot otomatis dari:

- 🌐 Website (full page / viewport)
- 🖥 Full desktop screen
- 🪟 Custom region
- 📱 Mobile device emulation
- 📤 Auto upload image

Dirancang untuk **developer, QA tester, automation scripts, dan content creators**.

Semua berjalan langsung dari terminal tanpa GUI.

---

# ✨ Features

## 🌐 Advanced Web Screenshot

Powered by **Playwright**

- 📜 Full-page scroll capture
- 📱 Mobile device emulation
- 🌙 Force dark mode
- 🧹 Auto remove ads & cookie banners
- 🧱 Hide elements via CSS selectors
- ⏳ Wait for dynamic elements
- 🔎 Custom viewport sizes
- 🧠 Smart domain filename detection

Example:

```bash
python src/ss.py --web https://example.com --full-page
```

---

## 🧹 Auto Clean Mode

Automatically removes intrusive UI elements like:

- Ads
- Cookie banners
- Popups
- Newsletter modals
- Floating chat widgets

Example:

```bash
python src/ss.py --web https://news-site.com --clean
```

---

## 📱 Device Emulation

Simulate mobile or tablet devices.

Example:

```bash
python src/ss.py --web https://example.com --mobile
```

Custom viewport:

```bash
python src/ss.py --web https://example.com --viewport-width 414 --viewport-height 896
```

---

## 🖥 Screen Capture

Capture your desktop or region.

Full screen:

```bash
python src/ss.py --full-screen
```

Region:

```bash
python src/ss.py --region 100 200 1200 800
```

---

## 📤 Auto Upload

Automatically upload screenshots to **Imgur**.

```bash
python src/ss.py --web https://github.com --upload
```

Returns shareable link instantly.

---

# ⚡ Quick Start

Clone repository:

```bash
git clone https://github.com/xosjslnks/auto-screenshot-cli.git
cd auto-screenshot-cli
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install Playwright browser:

```bash
playwright install chromium --with-deps
```

Run first screenshot:

```bash
python src/ss.py --web https://example.com --full-page
```

---

# 📊 Example Output

```
example.com_fullpage_2026-03-08_14-22-10.png
```

Or after upload:

```
Screenshot uploaded:
https://i.imgur.com/xxxxx.png
```

---

# 🖥 Platform Support

| Platform | Status |
|--------|--------|
| Windows | ✅ Supported |
| macOS | ✅ Supported |
| Linux | ✅ Supported |

---

# 🧠 Use Cases

Perfect for:

- 📊 Website documentation
- 🧪 UI testing
- 📱 Responsive layout testing
- 🐞 Bug reports
- 📸 Content creation
- 🤖 Automation scripts

---

# 🤝 Contributing

Pull requests are welcome.

Future ideas:

- 📂 Batch screenshot from file
- 📱 Android ADB screenshots
- 🎥 Video frame capture
- ☁ Cloud uploads (Google Drive / Dropbox)
- 📄 PDF export

---

# 📜 License

MIT License — free to use, modify, and distribute.

---

<p align="center">
Made with ❤️ by <b>xobe</b>
</p>

<p align="center">
⭐ If this project helped you, consider starring the repository!
</p>
