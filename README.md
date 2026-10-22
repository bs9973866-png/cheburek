# Cheburek Access

Windows desktop client for user-supplied proxy profiles and automatic discovery/testing of public community nodes.

> This project does not operate proxy servers. Public nodes are run by third parties, can disappear at any time and may observe connection metadata; avoid banking and sensitive accounts on unknown free proxies. Routing does not bypass phone verification or account eligibility checks.

## Automatic node discovery

Click **Автоподбор узла**. The application checks several public subscription mirrors, extracts supported VLESS/VMess/Trojan/Shadowsocks links, validates each candidate with sing-box, then attempts an HTTPS request through the local proxy. If one works, it imports the URI and starts the connection.

Network feeds used by the auto-discovery option:
- `morpheusadam/v2ray-config` mini bundle, via jsDelivr / raw mirrors
- `Au1rxx/free-vpn-subscriptions` V2Ray base64 feed, via jsDelivr

These are public third-party feeds, not a guarantee of free or stable service. The app tests from the user's connection, but a node can stop working seconds later. If all source mirrors are blocked, automatic discovery cannot fetch candidates.

## Windows executable

The GitHub Actions build downloads the official sing-box Windows amd64 release, verifies its SHA-256 digest, and bundles it inside `CheburekAccess.exe`; the app does not need to download the core from GitHub on first launch.

## Manual profile import

You can paste a supported VLESS / VMess / Trojan / Shadowsocks URI or import a sing-box JSON profile. The app uses the Windows system-proxy setting when enabled; some apps ignore it and may need separate configuration.

## Build from source

On Windows with Python 3.11+:

```powershell
py -m pip install -r requirements.txt
py app.py
```

To make a local executable after obtaining the official `sing-box.exe`:

```powershell
py -m pip install pyinstaller
pyinstaller --noconfirm --clean --onefile --windowed --name CheburekAccess --add-binary "sing-box.exe;." app.py
```

A GitHub Actions workflow builds the Windows executable and publishes it as a workflow artifact.
