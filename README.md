# Cheburek Access

Windows desktop client for managing a user-supplied sing-box/VLESS/Trojan/Shadowsocks proxy profile and applying domain-based routing for selected services.

> This project does not include proxy servers or provide accounts. Use a server/configuration you own or are authorized to use. Routing cannot bypass phone verification, account eligibility rules, or service-side restrictions.

## First build

The first version is a Windows GUI with service presets, imported proxy configuration, a local sing-box core installer, and optional Windows system-proxy switching. See the app for current limitations and setup instructions.

## Build

On Windows with Python 3.11+:

```powershell
py -m pip install -r requirements.txt
py app.py
```

Create a standalone executable:

```powershell
py -m pip install pyinstaller
pyinstaller --noconfirm --windowed --name CheburekAccess app.py
```

A GitHub Actions workflow will also build a Windows executable on push and make it available as a workflow artifact.
