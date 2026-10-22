# Cheburek Access

Windows desktop client for user-supplied proxy profiles and automatic discovery/testing of public community nodes.

> This project does not operate proxy servers. Public nodes are run by third parties, can disappear at any time and may observe connection metadata; avoid banking and sensitive accounts on unknown free proxies. Routing cannot bypass phone verification or account eligibility checks.

## Automatic node selection

Click **Автоподбор узла**. Current behavior:

1. Try a freshly generated sing-box JSON pool from the public Au1rxx feed. If it includes a `urltest` outbound, sing-box can auto-select/fail over among multiple nodes.
2. If the JSON pool cannot be used, pull the Morpheus `best.txt` and other public subscription mirrors.
3. Test the profile through a local mixed proxy using real HTTPS requests. Individual links are checked in parallel, and the app does not label a local port alone as a successful internet connection.

Supported link imports: VLESS, VMess, Trojan, Shadowsocks. XHTTP/SplitHTTP links are skipped because the bundled official upstream sing-box binary does not include the XHTTP extension. Public feeds can still contain dead or incompatible nodes; no public source can guarantee that a node will work on every ISP.

Public feeds:
- Au1rxx sing-box profile: `https://raw.githubusercontent.com/Au1rxx/free-vpn-subscriptions/main/output/singbox.json`
- Morpheus best-ranked list: `https://raw.githubusercontent.com/morpheusadam/v2ray-config/main/subs/bundles/best.txt`
- Mirrors are tried automatically if a primary source fails.

## Routing modes

- **Весь трафик (TUN)** sends non-local traffic through the selected outbound; administrator permission is required by Windows.
- **Только выбранные домены (TUN)** uses the service categories / custom domain list for split routing and otherwise goes direct.
- **Системный прокси (браузеры)** configures a localhost HTTP proxy; applications that ignore Windows proxy settings need TUN or their own proxy settings.

The app includes a categorized domain catalog, theme presets, custom-domain entry, saved UI preferences and an app icon.

## Security note

Public free proxy operators may observe traffic metadata, and profiles that set `allowInsecure=1` disable TLS certificate checks for that node. Never use unknown public nodes for private or sensitive accounts. Prefer a trusted server or provider for routine use.

## Windows executable

The GitHub Actions build downloads the official sing-box Windows amd64 release, verifies its SHA-256 digest, validates generated routing configs, bundles the executable and icon, and uploads `CheburekAccess.exe` as a workflow artifact.

## Build from source

On Windows with Python 3.11+:

```powershell
py -m pip install -r requirements.txt
py app.py
```

To make a local executable after obtaining the official `sing-box.exe`:

```powershell
py -m pip install pyinstaller pillow
python assets/generate_assets.py
pyinstaller --noconfirm --clean --onefile --windowed --name CheburekAccess --icon assets/cheburek.ico --add-binary "sing-box.exe;." --add-data "assets/cheburek.png;assets" app.py
```

GitHub Actions runs unit tests, checks the generated configuration with sing-box and publishes a Windows build.
