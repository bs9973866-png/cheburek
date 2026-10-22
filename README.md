# Cheburek Access

Windows desktop client for routing desktop-app and browser traffic through a user-supplied or publicly discovered sing-box proxy node.

## What's new

- Large editable domain catalog covering AI assistants, Telegram, WhatsApp/Meta, YouTube/Google, Discord, X, TikTok, Reddit, Spotify, streaming, developer tools, cloud/storage, productivity and games. Current presets include hundreds of unique domain suffixes.
- Three routing modes: **Весь трафик (TUN)** for apps that ignore Windows proxy settings, **Только выбранные домены (TUN)**, and **Системный прокси (браузеры)**.
- An original neon Cheburek icon, five live theme presets, save/restore of UI settings, scrollable service list, and manual custom domains.
- The connection state is only reported as successful after an HTTPS request succeeds through the configured outbound.
- CI validates all generated routing modes with the actual bundled sing-box binary, not only unit tests.

## TUN mode

TUN intercepts normal app traffic, including apps that ignore the Windows HTTP proxy settings. Windows requires administrator permission to create the tunnel; the app prompts for a UAC relaunch and restores the saved profile/preferences. Local/private LAN destinations remain direct. If you prefer not to grant administrator rights, switch to **Системный прокси (браузеры)**; that mode only affects applications that honor Windows' system-proxy settings.

## Automatic node discovery

Click **Автоподбор узла**. The application checks several public subscription mirrors, extracts supported VLESS/VMess/Trojan/Shadowsocks links, validates each candidate with sing-box, then attempts HTTPS through the selected node.

Public nodes are operated by third parties, can disappear at any time and may observe connection metadata. Do not use unknown public proxies for banking, passwords or sensitive accounts. Cheburek does not operate proxy servers and cannot bypass phone verification or eligibility rules for any service.

## Windows EXE

The GitHub Actions build downloads the pinned official sing-box Windows amd64 archive, verifies its SHA-256 digest, generates the icon assets, and bundles sing-box inside `CheburekAccess.exe`. The end-user app does not need to fetch the engine from GitHub on first launch.

Download the latest successful build from the repository's Actions tab: https://github.com/bs9973866-png/cheburek/actions

## Manual profile import

Paste a VLESS / VMess / Trojan / Shadowsocks URI or import a compatible sing-box JSON profile. Clash YAML and plain node lists are not sing-box JSON.

## Build from source

On Windows with Python 3.11+:

```powershell
py -m pip install -r requirements.txt
py assets/generate_assets.py
py app.py
```

Create a local executable after obtaining the official `sing-box.exe`:

```powershell
py -m pip install pyinstaller pillow
pyinstaller --noconfirm --clean --onefile --windowed --name CheburekAccess --icon assets/cheburek.ico --add-binary "sing-box.exe;." --add-data "assets/cheburek.png;assets" app.py
```

A GitHub Actions workflow validates the three routing modes and builds the Windows executable artifact.
