# Cheburek Access

Windows desktop client for managing a user-supplied sing-box/VLESS/Trojan/Shadowsocks proxy profile and applying domain-based routing for selected services.

> This project does not include proxy servers or provide accounts. Use a server/configuration you own or are authorized to use. Routing cannot bypass phone verification, account eligibility rules, or service-side restrictions.

## Windows executable

The GitHub Actions build now downloads the official sing-box Windows amd64 release, verifies its SHA-256 digest and bundles the binary inside `CheburekAccess.exe`. The end user therefore does not need the app to download sing-box from GitHub on first launch.

## Use

1. Download `CheburekAccess.exe` from the latest successful Actions run artifact.
2. Launch the app and paste a supported VLESS / VMess / Trojan / Shadowsocks URI, or import a sing-box JSON profile.
3. Select domains to route, then click **Подключить**.
4. When enabling system proxy, the app backs up and restores previous Windows proxy settings on disconnect/exit.

If using a custom build without a bundled core, choose **Выбрать sing-box.exe** and select `sing-box.exe` from the official sing-box release ZIP extracted on your PC.

The client uses the Windows system-proxy setting when enabled; applications that ignore the system proxy may require separate configuration. It does not include VPN servers or credentials.

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
