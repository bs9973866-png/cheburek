import base64
import ctypes
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
import queue
import random
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP_NAME = "Cheburek Access"
APP_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "CheburekAccess"
BIN_DIR = APP_DIR / "bin"
CORE = BIN_DIR / "sing-box.exe"
BUNDLED_CORE = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / "sing-box.exe"
CONFIG_PATH = APP_DIR / "active-config.json"
LOG_PATH = APP_DIR / "sing-box.log"
BACKUP_PATH = APP_DIR / "proxy-backup.json"
MIXED_PORT = 2080

SERVICES = {
    "OpenAI / Codex": [
        "openai.com", "chatgpt.com", "chat.openai.com", "auth.openai.com",
        "platform.openai.com", "api.openai.com", "oaistatic.com", "oaiusercontent.com",
        "files.oaiusercontent.com", "cdn.openai.com", "openaiapi-site.azureedge.net",
        "statsig.com", "featuregates.org", "intercom.io", "intercomcdn.com"
    ],
    "Claude / Anthropic": [
        "claude.ai", "anthropic.com", "claudeusercontent.com", "anthropicusercontent.com",
        "anthropic-static.com", "claudeassets.com", "claudeusercontent.net"
    ],
    "Google / Gemini / AI Studio": [
        "google.com", "googleapis.com", "gstatic.com", "googleusercontent.com",
        "googlevideo.com", "google-analytics.com", "googletagmanager.com", "googleadservices.com",
        "googleapis.cn", "googleusercontent.cn", "google.dev", "ai.google.dev",
        "gemini.google.com", "aistudio.google.com", "generativelanguage.googleapis.com",
        "makersuite.google.com", "notebooklm.google.com", "bard.google.com", "deepmind.google",
        "googlecloud.com", "cloud.google.com", "accounts.google.com", "ogs.google.com"
    ],
    "Telegram": [
        "telegram.org", "t.me", "telegram.me", "telegram.dog", "telegra.ph", "telesco.pe",
        "telegram-cdn.org", "cdn-telegram.org", "telegram.space", "tg.dev", "tx.me",
        "comments.app", "fragment.com", "ton.org"
    ],
    "WhatsApp / Meta": [
        "whatsapp.com", "whatsapp.net", "wa.me", "web.whatsapp.com", "whatsappbrand.com",
        "fb.com", "facebook.com", "facebook.net", "fbcdn.net", "fbsbx.com", "fb.watch",
        "messenger.com", "m.me", "instagram.com", "cdninstagram.com", "ig.me", "threads.net",
        "meta.ai", "meta.com", "oculus.com", "meta.net", "atdmt.com", "connect.facebook.net"
    ],
    "YouTube": [
        "youtube.com", "youtu.be", "googlevideo.com", "ytimg.com", "youtubei.googleapis.com",
        "youtube-nocookie.com", "youtubeeducation.com", "youtubekids.com", "youtubeembeddedplayer.googleapis.com",
        "youtube.googleapis.com", "ggpht.com", "googleusercontent.com", "widevine.com",
        "youtube-ui.l.google.com", "youtube.map.fastly.net", "yt3.ggpht.com"
    ],
    "Discord": [
        "discord.com", "discord.gg", "discordapp.com", "discordapp.net", "discord.media",
        "discordcdn.com", "discordstatus.com", "discord.new", "discord.gift", "discord.tools",
        "discordactivities.com", "discordsays.com", "discordmerch.com", "discord-attachments-uploads-prd.storage.googleapis.com"
    ],
    "X / Twitter": [
        "x.com", "twitter.com", "t.co", "twimg.com", "abs.twimg.com", "video.twimg.com",
        "pbs.twimg.com", "api.x.com", "api.twitter.com", "ads-twitter.com", "periscope.tv",
        "pscp.tv", "tweetdeck.com"
    ],
    "TikTok": [
        "tiktok.com", "tiktokv.com", "tiktokcdn.com", "tiktokcdn-us.com", "tiktokcdn-eu.com",
        "musical.ly", "muscdn.com", "byteoversea.com", "ibytedtos.com", "ibyteimg.com",
        "byteimg.com", "ttwstatic.com", "tiktokrow-cdn.com", "tiktokshop.com", "tiktokglobalshop.com",
        "snssdk.com", "pstatp.com", "toutiao.com", "capcut.com", "capcut.net"
    ],
    "Reddit": [
        "reddit.com", "redd.it", "redditmedia.com", "redditstatic.com", "redditinc.com",
        "reddithelp.com", "reddituploads.com", "redditblog.com", "redditchat.com"
    ],
    "Spotify / Music": [
        "spotify.com", "scdn.co", "spotifycdn.com", "spotifycdn.net", "pscdn.co",
        "audio-ak-spotify-com.akamaized.net", "spotify.design", "spotifynewsroom.jp",
        "deezer.com", "dzcdn.net", "music.youtube.com", "music.apple.com", "last.fm",
        "soundcloud.com", "sndcdn.com", "bandcamp.com", "mixcloud.com", "tidal.com"
    ],
    "GitHub / Developer tools": [
        "github.com", "githubusercontent.com", "githubassets.com", "github.io", "githubcopilot.com",
        "copilot.microsoft.com", "github.dev", "githubstatus.com", "github.community", "gitlab.com",
        "gitlab-static.net", "bitbucket.org", "atlassian.com", "stackoverflow.com", "stackexchange.com",
        "npmjs.com", "npmjs.org", "nodejs.org", "pypi.org", "pythonhosted.org", "rubygems.org",
        "crates.io", "rust-lang.org", "maven.org", "gradle.org", "docker.com", "docker.io",
        "hub.docker.com", "dev.azure.com", "visualstudio.com", "vscode.dev", "code.visualstudio.com",
        "jetbrains.com", "jetbrains.space", "replit.com", "codesandbox.io", "vercel.com", "netlify.app",
        "render.com", "fly.io", "railway.app", "cloudflare.com", "workers.dev", "pages.dev"
    ],
    "AI: Claude, Perplexity, DeepSeek, Mistral": [
        "perplexity.ai", "pplx.ai", "deepseek.com", "deepseek.ai", "chat.deepseek.com",
        "mistral.ai", "chat.mistral.ai", "labs.perplexity.ai", "grok.com", "x.ai",
        "cohere.com", "command-r.com", "you.com", "phind.com", "poe.com", "quora.com",
        "character.ai", "characterai.io", "janitorai.com", "jasper.ai", "writesonic.com",
        "copy.ai", "pi.ai", "inflection.ai", "blackbox.ai", "cursor.com", "windsurf.com",
        "codeium.com", "tabnine.com", "huggingface.co", "hf.co", "replicate.com", "runpod.io",
        "together.ai", "fireworks.ai", "groq.com", "cerebras.ai", "openrouter.ai", "siliconflow.com",
        "novita.ai", "fal.ai", "fal.run", "lmarena.ai", "arena.ai", "chat.lmsys.org"
    ],
    "Microsoft / Copilot": [
        "microsoft.com", "microsoftonline.com", "live.com", "bing.com", "bing.net",
        "copilot.microsoft.com", "copilot.com", "office.com", "office.net", "outlook.com",
        "windows.net", "azure.com", "azureedge.net", "azurefd.net", "msauth.net", "msftauth.net",
        "msidentity.com", "xbox.com", "xboxlive.com", "xboxservices.com", "skype.com",
        "teams.microsoft.com", "teams.live.com", "sharepoint.com", "onedrive.live.com",
        "1drv.com", "sfx.ms", "visualstudio.com", "aka.ms"
    ],
    "Streaming / Movies": [
        "netflix.com", "netflix.net", "nflxvideo.net", "nflximg.net", "nflxso.net",
        "nflxext.com", "disneyplus.com", "disney-plus.net", "disney.com", "dssott.com",
        "primevideo.com", "amazonvideo.com", "aiv-cdn.net", "hulu.com", "huluim.com",
        "max.com", "hbomax.com", "discoveryplus.com", "peacocktv.com", "paramountplus.com",
        "pluto.tv", "tubitv.com", "plex.tv", "crunchyroll.com", "vrv.co", "hidive.com",
        "funimation.com", "bilibili.com", "biliapi.net", "iqiyi.com", "youku.com", "viki.com",
        "dailymotion.com", "dmcdn.net", "vimeo.com", "vimeocdn.com", "twitch.tv", "ttvnw.net",
        "jtvnw.net", "ext-twitch.tv", "kick.com", "rumble.com", "odysee.com", "lbry.tv"
    ],
    "Gaming / Steam / Epic": [
        "steampowered.com", "steamcommunity.com", "steamstatic.com", "steamcontent.com",
        "steam-chat.com", "steamserver.net", "steamusercontent.com", "steamdeck.com",
        "epicgames.com", "epicgames.dev", "unrealengine.com", "fortnite.com", "eac-cdn.com",
        "ea.com", "origin.com", "eaassets-a.akamaihd.net", "battle.net", "blizzard.com",
        "blizzard.net", "riotgames.com", "leagueoflegends.com", "valorant.com", "riotcdn.net",
        "ubisoft.com", "ubi.com", "uplay.com", "rockstargames.com", "socialclub.rockstargames.com",
        "gog.com", "gog-statics.com", "itch.io", "itch.zone", "xbox.com", "xboxlive.com",
        "playstation.com", "playstation.net", "sonyentertainmentnetwork.com", "nintendo.com",
        "nintendo.net", "ea.com", "eaassets.com", "wargaming.net", "worldoftanks.com"
    ],
    "Minecraft / Roblox": [
        "minecraft.net", "mojang.com", "minecraftservices.com", "minecraft-services.net",
        "minecrafted.net", "minecraftprod.rustrician.net", "curseforge.com", "modrinth.com",
        "fabricmc.net", "papermc.io", "hangar.papermc.io", "spigotmc.org", "planetminecraft.com",
        "namemc.com", "optifine.net", "roblox.com", "rbxcdn.com", "roblox.cn", "rbx.com",
        "robloxdev.com", "robloxapi.com", "rbxtrk.com"
    ],
    "Messaging / Social": [
        "signal.org", "signal.art", "snapchat.com", "sc-cdn.net", "snapkit.com",
        "pinterest.com", "pinimg.com", "linkedin.com", "licdn.com", "tumblr.com", "tumblr.net",
        "flickr.com", "flickr.net", "mastodon.social", "bsky.app", "blueskyweb.xyz",
        "threads.net", "line.me", "line-apps.com", "kakao.com", "kakaocdn.net", "vk.com",
        "vk.ru", "userapi.com", "ok.ru", "odnoklassniki.ru", "weibo.com", "weibocdn.com",
        "wechat.com", "weixin.qq.com", "qq.com", "qpic.cn", "discord.com", "meetup.com"
    ],
    "Search / News": [
        "duckduckgo.com", "startpage.com", "brave.com", "search.brave.com", "ecosia.org",
        "yandex.com", "yandex.ru", "yastatic.net", "yandexcloud.net", "ya.ru", "rambler.ru",
        "proton.me", "protonmail.com", "protonvpn.com", "fastmail.com", "theguardian.com",
        "nytimes.com", "washingtonpost.com", "bbc.com", "bbc.co.uk", "reuters.com", "apnews.com",
        "bloomberg.com", "economist.com", "wired.com", "arstechnica.com", "techcrunch.com"
    ],
    "Cloud / Storage": [
        "dropbox.com", "dropboxapi.com", "dropboxusercontent.com", "box.com", "mega.io",
        "mega.nz", "mediafire.com", "wetransfer.com", "sendspace.com", "pcloud.com",
        "sync.com", "icloud.com", "icloud-content.com", "apple-cloudkit.com", "drive.google.com",
        "storage.googleapis.com", "blob.core.windows.net", "amazonaws.com", "cloudfront.net",
        "digitaloceanspaces.com", "backblazeb2.com", "wasabisys.com"
    ],
    "Design / Productivity": [
        "notion.so", "notion.site", "figma.com", "figmausercontent.com", "canva.com",
        "canva-apps.com", "miro.com", "linear.app", "asana.com", "trello.com", "slack.com",
        "slack-edge.com", "zoom.us", "zoom.com", "webex.com", "grammarly.com", "grammarly.io",
        "medium.com", "substack.com", "readwise.io", "evernote.com", "todoist.com", "calendly.com",
        "typeform.com", "airtable.com", "monday.com", "clickup.com", "obsidian.md"
    ],
    "Apple services": [
        "apple.com", "icloud.com", "apple-cloudkit.com", "mzstatic.com", "itunes.apple.com",
        "apps.apple.com", "appstore.com", "apple.news", "apple-dns.net", "cdn-apple.com",
        "push.apple.com", "identity.apple.com"
    ]
}

THEMES = {
    "Neon Pink": {"bg": "#101017", "panel": "#1a1822", "panel2": "#24202e", "fg": "#f7f2fb", "muted": "#b1a7bd", "accent": "#ff3f83", "green": "#46dda0", "border": "#473044"},
    "Ocean": {"bg": "#09121b", "panel": "#101f2c", "panel2": "#183044", "fg": "#ecf7ff", "muted": "#91b0c5", "accent": "#23b8e6", "green": "#4bd6b0", "border": "#284a5f"},
    "Emerald": {"bg": "#0c1512", "panel": "#14231d", "panel2": "#1d332a", "fg": "#eefbf4", "muted": "#94b5a2", "accent": "#2dd4a3", "green": "#73e6a3", "border": "#2f5949"},
    "Amber": {"bg": "#17110a", "panel": "#251a10", "panel2": "#342416", "fg": "#fff7eb", "muted": "#c5a88b", "accent": "#ffad39", "green": "#7be0a1", "border": "#5a3f27"},
    "Mono": {"bg": "#101010", "panel": "#1b1b1b", "panel2": "#272727", "fg": "#f5f5f5", "muted": "#aaaaaa", "accent": "#eeeeee", "green": "#72d69b", "border": "#3b3b3b"}
}
BG = "#111318"
PANEL = "#1a1d24"
PANEL_2 = "#20242d"
FG = "#f2f3f7"
MUTED = "#9ca3b4"
ACCENT = "#ff4f64"
GREEN = "#45d483"
BORDER = "#343a46"

# Public, third-party sources. JSON profiles are tried first because their urltest
# groups can select a live node without blindly trusting the first N links.
PUBLIC_PROFILE_FEEDS = [
    "https://cdn.jsdelivr.net/gh/Au1rxx/free-vpn-subscriptions@main/output/singbox.json",
    "https://ghproxy.net/https://raw.githubusercontent.com/Au1rxx/free-vpn-subscriptions/main/output/singbox.json",
    "https://gh-proxy.com/https://raw.githubusercontent.com/Au1rxx/free-vpn-subscriptions/main/output/singbox.json",
    "https://raw.githubusercontent.com/Au1rxx/free-vpn-subscriptions/main/output/singbox.json",
]
PUBLIC_NODE_FEEDS = [
    "https://cdn.jsdelivr.net/gh/morpheusadam/v2ray-config@main/subs/bundles/best.txt",
    "https://ghproxy.net/https://raw.githubusercontent.com/morpheusadam/v2ray-config/main/subs/bundles/best.txt",
    "https://raw.githack.com/morpheusadam/v2ray-config/main/subs/bundles/best.txt",
    "https://raw.githubusercontent.com/morpheusadam/v2ray-config/main/subs/bundles/best.txt",
    "https://raw.githubusercontent.com/morpheusadam/v2ray-config/main/subs/bundles/all.txt",
    "https://cdn.jsdelivr.net/gh/morpheusadam/v2ray-config@main/subs/bundles/all.txt",
    "https://raw.githubusercontent.com/morpheusadam/v2ray-config/main/subs/bundles/all-base64.txt",
    "https://cdn.jsdelivr.net/gh/morpheusadam/v2ray-config@main/subs/bundles/all-base64.txt",
    "https://raw.githack.com/morpheusadam/v2ray-config/main/subs/bundles/best.txt",
    "https://ghproxy.net/https://raw.githubusercontent.com/morpheusadam/v2ray-config/main/subs/bundles/best.txt",
    "https://gh-proxy.com/https://raw.githubusercontent.com/morpheusadam/v2ray-config/main/subs/bundles/best.txt",
    "https://raw.githubusercontent.com/morpheusadam/v2ray-config/main/subs/bundles/mini.txt",
    "https://cdn.jsdelivr.net/gh/Au1rxx/free-vpn-subscriptions@main/output/v2ray-base64.txt",
    "https://ghproxy.net/https://raw.githubusercontent.com/Au1rxx/free-vpn-subscriptions/main/output/v2ray-base64.txt",
]
SUPPORTED_NODE_SCHEMES = ("vless://", "vmess://", "trojan://", "ss://", "hy2://", "hysteria2://")
PROBE_CONFIG_PATH = APP_DIR / "probe-config.json"
AUTO_PROFILE_PATH = APP_DIR / "auto-profile.json"
AUTO_PROFILE_TOKEN = "::CHEBUREK_AUTO_PROFILE::"
MAX_FEED_BYTES = 30_000_000


def extract_profile_candidates(body):
    """Read either a complete sing-box JSON config or a plain/base64 subscription."""
    body = body.lstrip("\ufeff").strip()
    candidates = []
    if body.startswith("{"):
        try:
            data = json.loads(body)
            if isinstance(data, dict) and isinstance(data.get("outbounds"), list) and data["outbounds"]:
                candidates.append(json.dumps(data, ensure_ascii=False))
        except Exception:
            pass
    candidates.extend(extract_proxy_uris(body))
    return list(dict.fromkeys(candidates))


def extract_proxy_uris(body):
    """Extract supported public proxy URIs from plain-text or base64 subscriptions."""
    body = body.lstrip("\ufeff").strip()
    if not body:
        return []
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    found = []
    for line in lines:
        candidate = line if line.lower().startswith(SUPPORTED_NODE_SCHEMES) else line.split("#", 1)[0]
        if candidate.lower().startswith(SUPPORTED_NODE_SCHEMES) and len(candidate) <= 8192:
            found.append(candidate)
    if not found and len(body) <= MAX_FEED_BYTES:
        compact = "".join(body.split())
        if re.fullmatch(r"[A-Za-z0-9_+/=-]+", compact or ""):
            try:
                decoded = base64.urlsafe_b64decode(compact + "=" * ((4 - len(compact) % 4) % 4)).decode("utf-8", "ignore")
                for line in decoded.splitlines():
                    line = line.strip()
                    if line.lower().startswith(SUPPORTED_NODE_SCHEMES) and len(line) <= 8192:
                        found.append(line)
            except Exception:
                pass
    deduped = []
    seen = set()
    for uri in found:
        if uri not in seen:
            seen.add(uri)
            deduped.append(uri)
    return deduped


def url_query(parsed):
    return {k: v[-1] for k, v in urllib.parse.parse_qs(parsed.query, keep_blank_values=True).items()}


def parse_uri(raw):
    raw = raw.strip()
    if not raw:
        raise ValueError("Вставь ссылку VLESS/Trojan/SS/VMess или импортируй sing-box JSON.")
    if raw.startswith("{"):
        data = json.loads(raw)
        if not isinstance(data, dict) or not isinstance(data.get("outbounds"), list):
            raise ValueError("В JSON не найден список outbounds. Нужен профиль sing-box.")
        return data, True

    scheme = raw.split(":", 1)[0].lower()
    if scheme == "vmess":
        token = raw.split("://", 1)[1].split("#", 1)[0].strip()
        token += "=" * ((4 - len(token) % 4) % 4)
        try:
            d = json.loads(base64.urlsafe_b64decode(token).decode("utf-8"))
        except Exception as exc:
            raise ValueError("Не удалось прочитать VMess-ссылку.") from exc
        server = d.get("add")
        port = int(d.get("port", 0))
        uid = d.get("id")
        if not server or not port or not uid:
            raise ValueError("В VMess-ссылке не хватает сервера, порта или UUID.")
        outbound = {"type": "vmess", "tag": "proxy", "server": server,
                    "server_port": port, "uuid": uid, "alter_id": int(d.get("aid", 0)),
                    "security": d.get("scy", "auto")}
        if str(d.get("tls", "")).lower() == "tls":
            outbound["tls"] = {"enabled": True, "server_name": d.get("sni") or d.get("host") or server,
                               "utls": {"enabled": True, "fingerprint": "chrome"}}
            if str(d.get("allowInsecure", "false")).lower() in ("1", "true", "yes"):
                outbound["tls"]["insecure"] = True
        net = str(d.get("net", "tcp")).lower()
        if net in ("xhttp", "splithttp"):
            raise ValueError("Этот VMess узел использует XHTTP, которого нет в официальном sing-box; пробую следующий.")
        if net not in ("tcp", "raw", "ws", "grpc"):
            raise ValueError(f"Неподдерживаемый VMess транспорт {net}; пропускаю этот узел.")
        if net == "ws":
            outbound["transport"] = {"type": "ws", "path": d.get("path") or "/"}
            if d.get("host"):
                outbound["transport"]["headers"] = {"Host": d["host"]}
        elif net == "grpc":
            outbound["transport"] = {"type": "grpc", "service_name": d.get("path") or ""}
        return {"outbounds": [outbound]}, False

    parsed = urllib.parse.urlsplit(raw)
    q = url_query(parsed)
    host, port = parsed.hostname, parsed.port
    # SIP002 Shadowsocks can encode the entire method:password@host:port authority in base64.
    if (not host or not port) and scheme != "ss":
        raise ValueError("В ссылке должны быть указаны адрес сервера и порт.")

    if scheme in ("hy2", "hysteria2"):
        password = urllib.parse.unquote(parsed.username or parsed.password or "")
        if not password:
            raise ValueError("В Hysteria2-ссылке не найден пароль.")
        tls = {
            "enabled": True,
            "server_name": q.get("sni") or q.get("peer") or host,
        }
        if q.get("insecure", q.get("allowInsecure", "0")).lower() in ("1", "true", "yes"):
            tls["insecure"] = True
        if q.get("alpn"):
            tls["alpn"] = q["alpn"].split(",")
        outbound = {
            "type": "hysteria2",
            "tag": "proxy",
            "server": host,
            "server_port": port,
            "password": password,
            "tls": tls
        }
        obfs_type = q.get("obfs")
        obfs_password = q.get("obfs-password") or q.get("obfs_password")
        if obfs_type and obfs_type.lower() not in ("", "none"):
            if not obfs_password:
                raise ValueError("В Hysteria2-ссылке задан obfs, но не задан obfs-password.")
            outbound["obfs"] = {"type": obfs_type, "password": obfs_password}
        return {"outbounds": [outbound]}, False

    if scheme == "vless":
        uid = urllib.parse.unquote(parsed.username or "")
        if not uid:
            raise ValueError("В VLESS-ссылке не найден UUID.")
        out = {"type": "vless", "tag": "proxy", "server": host, "server_port": port, "uuid": uid}
        flow = q.get("flow")
        if flow:
            out["flow"] = flow
        security = q.get("security", "none").lower()
        if security in ("tls", "reality"):
            tls = {"enabled": True, "server_name": q.get("sni") or q.get("serverName") or host,
                   "utls": {"enabled": True, "fingerprint": q.get("fp", "chrome")}}
            if q.get("allowInsecure", "").lower() in ("1", "true", "yes"):
                tls["insecure"] = True
            if q.get("alpn"):
                tls["alpn"] = q["alpn"].split(",")
            if security == "reality":
                public_key = q.get("pbk") or q.get("publicKey")
                short_id = q.get("sid") or q.get("shortId", "")
                if not public_key:
                    raise ValueError("Для VLESS Reality в ссылке должен быть параметр pbk (public key).")
                tls["reality"] = {"enabled": True, "public_key": public_key, "short_id": short_id}
            out["tls"] = tls
        add_transport(out, q)
        return {"outbounds": [out]}, False

    if scheme == "trojan":
        password = urllib.parse.unquote(parsed.username or "")
        if not password:
            raise ValueError("В Trojan-ссылке не найден пароль.")
        out = {"type": "trojan", "tag": "proxy", "server": host, "server_port": port,
               "password": password, "tls": {"enabled": q.get("security", "tls") != "none",
                                              "server_name": q.get("sni") or q.get("peer") or host,
                                              "utls": {"enabled": True, "fingerprint": q.get("fp", "chrome")}}}
        if q.get("allowInsecure", "").lower() in ("1", "true", "yes"):
            out["tls"]["insecure"] = True
        add_transport(out, q)
        return {"outbounds": [out]}, False

    if scheme == "ss":
        # SIP002 forms include encoded method:password@host:port and separate method:password.
        parsed_user = urllib.parse.unquote(parsed.username or "")
        parsed_password = urllib.parse.unquote(parsed.password or "")
        if host and port and parsed_password:
            method, password = parsed_user, parsed_password
        else:
            user = parsed_user
            try:
                if ":" not in user:
                    token = user + "=" * ((4 - len(user) % 4) % 4)
                    user = base64.urlsafe_b64decode(token).decode("utf-8")
            except Exception:
                pass
            if ":" not in user or "@" in user:
                # Base64 payload may contain the full userinfo@host:port, not just method:password.
                payload = raw.split("://", 1)[1].split("#", 1)[0]
                payload = urllib.parse.unquote(payload)
                payload += "=" * ((4 - len(payload) % 4) % 4)
                try:
                    decoded = base64.urlsafe_b64decode(payload).decode("utf-8")
                    p2 = urllib.parse.urlsplit("ss://" + decoded)
                    host, port = p2.hostname, p2.port
                    method = urllib.parse.unquote(p2.username or "")
                    password = urllib.parse.unquote(p2.password or "")
                    if not method or not password or not host or not port:
                        raise ValueError("Incomplete SIP002 profile.")
                    user = ""
                except Exception as exc:
                    raise ValueError("Не удалось разобрать Shadowsocks URI. Попробуй импорт sing-box JSON.") from exc
            if user:
                if ":" not in user:
                    raise ValueError("В SS-ссылке не распознаны method:password.")
                method, password = user.split(":", 1)
        out = {"type": "shadowsocks", "tag": "proxy", "server": host, "server_port": port,
               "method": method, "password": password}
        return {"outbounds": [out]}, False

    raise ValueError("Поддерживаются vless://, vmess://, trojan://, ss:// и sing-box JSON.")


def add_transport(out, q):
    kind = q.get("type", "tcp").lower()
    path = urllib.parse.unquote(q.get("path", "/"))
    host_header = q.get("host")
    if kind in ("tcp", "raw", ""):
        # No special transport block means standard TCP.
        return
    if kind == "ws":
        transport = {"type": "ws", "path": path}
        if host_header:
            transport["headers"] = {"Host": host_header}
        out["transport"] = transport
    elif kind in ("grpc", "gun"):
        out["transport"] = {"type": "grpc", "service_name": q.get("serviceName", "")}
    elif kind in ("httpupgrade", "http-upgrade"):
        transport = {"type": "httpupgrade", "path": path}
        if host_header:
            transport["host"] = [host_header]
        out["transport"] = transport
    elif kind in ("xhttp", "splithttp"):
        raise ValueError("Этот узел использует XHTTP, которого нет в официальном sing-box внутри приложения; пробую следующий узел.")
    else:
        raise ValueError(f"Неподдерживаемый транспорт {kind}; пропускаю этот узел.")


def proxy_tag_for(config):
    outbounds = config.get("outbounds", [])
    # Prefer the published auto-testing pool over the first individual node.
    for desired in ("urltest", "selector"):
        choices = [ob for ob in outbounds if ob.get("type") == desired and ob.get("tag")]
        if choices:
            # Prefer conventional auto/proxy tags, then retain source order.
            choices.sort(key=lambda ob: (
                0 if ob.get("tag", "").lower() in {"auto", "urltest", "best", "proxy", "select", "manual"} else 1,
                ob.get("tag", "").lower() not in {"auto", "urltest", "best"}
            ))
            return choices[0]["tag"]
    preferred = {"vless", "vmess", "trojan", "shadowsocks", "socks", "http", "hysteria", "hysteria2", "tuic", "wireguard"}
    for ob in outbounds:
        if ob.get("type") in preferred and ob.get("tag"):
            return ob["tag"]
    for ob in outbounds:
        if ob.get("tag") and ob.get("type") not in {"direct", "block", "dns"}:
            return ob["tag"]
    raise ValueError("В конфиге не найден исходящий прокси (outbound).")


def make_routing_config(data, enabled_services, custom_domains, mode="Весь трафик (TUN)", inbound_port=MIXED_PORT):
    """Build a current sing-box 1.14-compatible config for system proxy or device-wide TUN."""
    config = json.loads(json.dumps(data))
    outbounds = config.setdefault("outbounds", [])
    if not any(o.get("tag") == "direct" for o in outbounds):
        outbounds.append({"type": "direct", "tag": "direct"})
    proxy_tag = proxy_tag_for(config)

    # The mixed inbound remains available on loopback for upstream health checks in every mode.
    mixed_inbound = {
        "type": "mixed",
        "tag": "cheburek-mixed",
        "listen": "127.0.0.1",
        "listen_port": inbound_port
    }
    if mode in ("Весь трафик (TUN)", "Только выбранные домены (TUN)"):
        config["inbounds"] = [{
            "type": "tun",
            "tag": "cheburek-tun",
            "interface_name": "Cheburek",
            "address": ["172.19.0.1/30", "fdfe:dcba:9876::1/126"],
            "auto_route": True,
            "strict_route": True,
            "stack": "mixed",
            "dns_mode": "hijack"
        }, mixed_inbound]
    else:
        config["inbounds"] = [mixed_inbound]

    route = config.setdefault("route", {})
    # Build routing rules ourselves so imported defaults do not silently override the chosen mode.
    rules = []
    if mode in ("Весь трафик (TUN)", "Только выбранные домены (TUN)"):
        rules.append({"action": "sniff"})
        # Keep local devices and LAN services reachable instead of sending private IPs outside.
        rules.append({"ip_is_private": True, "action": "route", "outbound": "direct"})

    # Health-check traffic is explicitly routed through the selected proxy in every mode.
    rules.append({
        "domain_suffix": ["cp.cloudflare.com", "example.com", "www.gstatic.com", "www.microsoft.com"],
        "action": "route",
        "outbound": proxy_tag
    })
    all_domains = []
    for name in enabled_services:
        all_domains.extend(SERVICES.get(name, []))
    if custom_domains:
        all_domains.extend(d.strip().lower().lstrip(".") for d in re.split(r"[,;\s]+", custom_domains) if d.strip())
    domains = sorted(set(d.strip().lower().lstrip(".") for d in all_domains if d.strip()))
    invalid = [d for d in domains if not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?", d) or ".." in d]
    if invalid:
        raise ValueError("Некорректный домен: " + invalid[0])

    # Split mode routes selected domain suffixes through the proxy on every app, not just browsers.
    # Full-tunnel mode sends all non-LAN traffic to the proxy, which also handles native apps
    # that ignore Windows' HTTP proxy settings (e.g. many Telegram/WhatsApp builds).
    if mode != "Весь трафик (TUN)" and domains:
        rules.append({
            "domain_suffix": domains,
            "action": "route",
            "outbound": proxy_tag
        })

    route["rules"] = rules
    route["auto_detect_interface"] = True
    if mode == "Весь трафик (TUN)":
        route["final"] = proxy_tag
    else:
        route["final"] = "direct"
    config["outbounds"] = outbounds
    return config


def make_probe_config(data, enabled_services, custom_domains, inbound_port=MIXED_PORT):
    """Build a temporary mixed-inbound config, forcing probe destinations through the tested proxy."""
    config = make_routing_config(data, enabled_services, custom_domains, "Системный прокси (браузеры)", inbound_port=inbound_port)
    route = config.setdefault("route", {})
    rules = route.setdefault("rules", [])
    if not isinstance(rules, list):
        rules = []
        route["rules"] = rules
    rules.insert(0, {
        "domain_suffix": ["cp.cloudflare.com", "example.com", "www.gstatic.com", "www.microsoft.com"],
        "action": "route",
        "outbound": proxy_tag_for(config),
    })
    return config


def ensure_app_dir():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    BIN_DIR.mkdir(parents=True, exist_ok=True)


def ensure_core_available():
    """Install the build-bundled sing-box core into the per-user app directory."""
    ensure_app_dir()
    if not CORE.exists() and BUNDLED_CORE.is_file():
        shutil.copy2(BUNDLED_CORE, CORE)


def get_registry_values():
    import winreg
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    names = ("ProxyEnable", "ProxyServer", "ProxyOverride")
    values = {}
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
        for name in names:
            try:
                values[name] = winreg.QueryValueEx(key, name)[0]
            except FileNotFoundError:
                values[name] = None
    return values


def write_registry_values(values):
    import winreg
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
        for name, value in values.items():
            try:
                if value is None:
                    winreg.DeleteValue(key, name)
                else:
                    value_type = winreg.REG_DWORD if name == "ProxyEnable" else winreg.REG_SZ
                    winreg.SetValueEx(key, name, 0, value_type, value)
            except FileNotFoundError:
                pass
    try:
        import ctypes
        internet_set_option = ctypes.windll.Wininet.InternetSetOptionW
        internet_set_option(None, 39, None, 0)  # INTERNET_OPTION_SETTINGS_CHANGED
        internet_set_option(None, 37, None, 0)  # INTERNET_OPTION_REFRESH
    except Exception:
        pass


def restore_if_stale():
    if not BACKUP_PATH.exists():
        return
    try:
        backup = json.loads(BACKUP_PATH.read_text(encoding="utf-8"))
        current = get_registry_values()
        proxy_server = str(current.get("ProxyServer") or "")
        if "127.0.0.1:2080" in proxy_server or "localhost:2080" in proxy_server:
            write_registry_values(backup)
        BACKUP_PATH.unlink(missing_ok=True)
    except Exception:
        pass


def is_admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def resource_path(relative):
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / relative


class CheburekApp:
    def __init__(self, root):
        self.root = root
        ensure_app_dir()
        ensure_core_available()
        restore_if_stale()
        self.state_path = APP_DIR / "ui-state.json"
        self.saved_state = {}
        try:
            self.saved_state = json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception:
            self.saved_state = {}
        self.restore_admin = "--restore-admin" in sys.argv[1:]
        self.process = None
        self.proxy_changed = False
        self.loaded_path = ""
        self.busy = False
        self.status_var = tk.StringVar(value="Отключено")
        self.profile_var = tk.StringVar(value="Профиль не загружен")
        self.use_system_proxy = tk.BooleanVar(value=bool(self.saved_state.get("use_system_proxy", True)))
        self.mode_var = tk.StringVar(value=self.saved_state.get("mode", "Весь трафик (TUN)"))
        self.theme_var = tk.StringVar(value=self.saved_state.get("theme", "Neon Pink"))
        selected = set(self.saved_state.get("selected_services", SERVICES.keys()))
        self.service_vars = {name: tk.BooleanVar(value=name in selected) for name in SERVICES}
        self._set_global_theme(self.theme_var.get())
        self._style()
        self._build()
        self._restore_ui_state()
        self.apply_theme(self.theme_var.get(), initial=True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(400, self.refresh_core_state)
        if self.restore_admin:
            self.root.after(900, self.connect)

    def _style(self):
        self.root.title(APP_NAME)
        self.root.geometry("1180x860")
        self.root.minsize(1000, 740)
        self.root.configure(bg=BG)
        try:
            icon_file = resource_path("assets/cheburek.png")
            if icon_file.is_file():
                self.window_icon = tk.PhotoImage(file=str(icon_file))
                self.root.iconphoto(True, self.window_icon)
        except Exception:
            self.window_icon = None
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=PANEL)
        style.configure("TLabel", background=BG, foreground=FG, font=("Segoe UI", 10))
        style.configure("Card.TLabel", background=PANEL, foreground=FG, font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=PANEL, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("Title.TLabel", background=BG, foreground=FG, font=("Segoe UI Semibold", 23))
        style.configure("Section.TLabel", background=PANEL, foreground=FG, font=("Segoe UI Semibold", 12))
        style.configure("TButton", background=PANEL_2, foreground=FG, padding=(12, 8), borderwidth=0, font=("Segoe UI Semibold", 9))
        style.map("TButton", background=[("active", "#343a48"), ("disabled", "#242831")], foreground=[("disabled", "#777d8c")])
        style.configure("Accent.TButton", background=ACCENT, foreground="#ffffff")
        style.map("Accent.TButton", background=[("active", "#ff6b7b")])
        style.configure("TCheckbutton", background=PANEL, foreground=FG, font=("Segoe UI", 10))
        style.map("TCheckbutton", background=[("active", PANEL)], foreground=[("disabled", MUTED)])
        style.configure("TEntry", fieldbackground=PANEL_2, foreground=FG, insertcolor=FG, borderwidth=0, padding=6)
        style.configure("TCombobox", fieldbackground=PANEL_2, foreground=FG, padding=6)
        style.configure("Horizontal.TProgressbar", background=ACCENT, troughcolor=PANEL_2, bordercolor=PANEL_2)
        style.configure("TCombobox", fieldbackground=PANEL_2, background=PANEL_2, foreground=FG, arrowcolor=ACCENT)
        style.map("TCombobox", fieldbackground=[("readonly", PANEL_2)], foreground=[("readonly", FG)])

    def _set_global_theme(self, name):
        global BG, PANEL, PANEL_2, FG, MUTED, ACCENT, GREEN, BORDER
        palette = THEMES.get(name, THEMES["Neon Pink"])
        BG = palette["bg"]
        PANEL = palette["panel"]
        PANEL_2 = palette["panel2"]
        FG = palette["fg"]
        MUTED = palette["muted"]
        ACCENT = palette["accent"]
        GREEN = palette["green"]
        BORDER = palette["border"]

    def apply_theme(self, selected=None, initial=False):
        selected = selected or self.theme_var.get()
        old = {"bg": BG, "panel": PANEL, "panel2": PANEL_2, "fg": FG,
               "muted": MUTED, "accent": ACCENT, "green": GREEN, "border": BORDER}
        self.theme_var.set(selected if selected in THEMES else "Neon Pink")
        self._set_global_theme(self.theme_var.get())
        palette_map = {
            old["bg"]: BG, old["panel"]: PANEL, old["panel2"]: PANEL_2,
            old["fg"]: FG, old["muted"]: MUTED, old["accent"]: ACCENT,
            old["green"]: GREEN, old["border"]: BORDER,
            "#271920": PANEL, "#63303e": BORDER, "#ff9eac": ACCENT,
            "#f4dfe3": FG, "#343a48": BORDER, "#242831": PANEL_2,
            "#777d8c": MUTED,
        }
        self._style()
        if not initial:
            def recolor(widget):
                for opt in ("background", "bg", "foreground", "fg", "highlightbackground",
                            "insertbackground", "selectbackground", "troughcolor", "bordercolor"):
                    try:
                        value = widget.cget(opt)
                        if isinstance(value, str) and value.lower() in palette_map:
                            widget.configure(**{opt: palette_map[value.lower()]})
                    except Exception:
                        pass
                for child in widget.winfo_children():
                    recolor(child)
            recolor(self.root)
        try:
            self.status_pill.configure(bg=PANEL_2)
        except Exception:
            pass
        self._save_state()
        self.root.update_idletasks()

    def select_all_services(self):
        for variable in self.service_vars.values():
            variable.set(True)
        self._save_state()

    def clear_all_services(self):
        for variable in self.service_vars.values():
            variable.set(False)
        self._save_state()

    def _restore_ui_state(self):
        state = self.saved_state or {}
        profile = state.get("profile", "")
        self.auto_profile_active = bool(state.get("auto_profile", False)) and AUTO_PROFILE_PATH.is_file()
        if self.auto_profile_active or profile == AUTO_PROFILE_TOKEN:
            self.auto_profile_active = AUTO_PROFILE_PATH.is_file()
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", "Автоматический профиль sing-box\nПул публичных узлов сохранён локально. Нажми «Подключиться» для повторного использования.")
            self.profile_var.set(state.get("profile_label", "Автопрофиль восстановлен локально"))
        elif profile:
            self.auto_profile_active = False
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", profile)
            self.profile_var.set(state.get("profile_label", "Профиль восстановлен локально"))
        else:
            self.auto_profile_active = False
        domains = state.get("custom_domains", "")
        if domains:
            self.custom_entry.insert(0, domains)
        if state.get("loaded_path"):
            self.loaded_path = state["loaded_path"]

    def _manual_profile_edit(self, _event=None):
        if getattr(self, "auto_profile_active", False):
            self.auto_profile_active = False
            self.loaded_path = ""
            self.profile_var.set("Ручной профиль")
            self._save_state()

    def _save_state(self):
        try:
            profile_text = AUTO_PROFILE_TOKEN if getattr(self, "auto_profile_active", False) else (
                self.editor.get("1.0", "end").strip() if hasattr(self, "editor") else ""
            )
            state = {
                "profile": profile_text,
                "auto_profile": bool(getattr(self, "auto_profile_active", False)),
                "profile_label": self.profile_var.get() if hasattr(self, "profile_var") else "",
                "custom_domains": self.custom_entry.get().strip() if hasattr(self, "custom_entry") else "",
                "mode": self.mode_var.get() if hasattr(self, "mode_var") else "Весь трафик (TUN)",
                "theme": self.theme_var.get() if hasattr(self, "theme_var") else "Neon Pink",
                "use_system_proxy": self.use_system_proxy.get() if hasattr(self, "use_system_proxy") else True,
                "selected_services": [name for name, var in self.service_vars.items() if var.get()],
                "loaded_path": self.loaded_path,
            }
            self.state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def restart_as_admin(self):
        self._save_state()
        try:
            if getattr(sys, "frozen", False):
                executable = sys.executable
                params = "--restore-admin"
            else:
                executable = sys.executable
                params = subprocess.list2cmdline([str(Path(__file__).resolve()), "--restore-admin"])
            result = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", executable, params, str(Path.cwd()), 1
            )
            if result > 32:
                self.root.after(150, self.root.destroy)
                return
            messagebox.showerror("Не удалось запустить с правами администратора",
                                 "Windows не запустила повышенный процесс. Попробуй закрыть программу и открыть её через «Запуск от имени администратора».")
        except Exception as exc:
            messagebox.showerror("Ошибка UAC", str(exc))

    def _build(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=22, pady=(14, 11))
        brand = tk.Frame(header, bg=BG)
        brand.pack(side="left", fill="x", expand=True)
        try:
            icon_path = resource_path("assets/cheburek.png")
            if icon_path.is_file():
                self.logo_img = tk.PhotoImage(file=str(icon_path)).subsample(5, 5)
                tk.Label(brand, image=self.logo_img, bg=BG, bd=0).pack(side="left", padx=(0, 12))
        except Exception:
            self.logo_img = None
        brand_text = tk.Frame(brand, bg=BG)
        brand_text.pack(side="left", anchor="w")
        tk.Label(brand_text, text="CHEBUREK", bg=BG, fg=ACCENT, font=("Segoe UI Black", 24)).pack(anchor="w")
        tk.Label(brand_text, text="ACCESS  •  интернет-маршрутизация", bg=BG, fg=MUTED,
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 2))

        theme_box = tk.Frame(header, bg=BG)
        theme_box.pack(side="right", padx=(10, 14), pady=4)
        tk.Label(theme_box, text="ТЕМА", bg=BG, fg=MUTED, font=("Segoe UI Semibold", 8)).pack(anchor="w")
        self.theme_combo = ttk.Combobox(theme_box, textvariable=self.theme_var, values=list(THEMES.keys()),
                                        state="readonly", width=12)
        self.theme_combo.pack()
        self.theme_combo.bind("<<ComboboxSelected>>", lambda _event: self.apply_theme())

        self.status_pill = tk.Label(header, textvariable=self.status_var, bg=PANEL_2, fg=MUTED,
                                    font=("Segoe UI Semibold", 10), padx=13, pady=8)
        self.status_pill.pack(side="right", anchor="ne", pady=9)

        banner = tk.Frame(self.root, bg="#271920", highlightbackground="#63303e", highlightthickness=1)
        banner.pack(fill="x", padx=22, pady=(0, 14))
        tk.Label(banner, text="ВНИМАНИЕ", bg="#271920", fg="#ff9eac", font=("Segoe UI Semibold", 9)).pack(
            side="left", padx=(12, 8), pady=10)
        tk.Label(banner, text="Нет своего профиля? Нажми «Автоподбор узла»: программа скачает публичные узлы и проверит их с твоего ПК. Это сторонние серверы — не используй их для банков и чувствительных аккаунтов. Проверку телефона Codex они не обходят.",
                 bg="#271920", fg="#f4dfe3", font=("Segoe UI", 9), anchor="w", wraplength=850, justify="left").pack(
            side="left", fill="x", expand=True, padx=(0, 10), pady=8)

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=22, pady=(0, 14))
        left = tk.Frame(body, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.configure(width=320)
        left.pack_propagate(False)
        right = tk.Frame(body, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="МАРШРУТИЗАЦИЯ", bg=PANEL, fg=FG, font=("Segoe UI Semibold", 12)).pack(
            anchor="w", padx=16, pady=(14, 4))
        tk.Label(left, text=f"Каталог: {len(SERVICES)} категорий / {len(set(d for ds in SERVICES.values() for d in ds))} доменов",
                 bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(0, 7))
        service_buttons = tk.Frame(left, bg=PANEL)
        service_buttons.pack(fill="x", padx=13, pady=(0, 3))
        ttk.Button(service_buttons, text="Выбрать всё", command=self.select_all_services).pack(side="left")
        ttk.Button(service_buttons, text="Снять всё", command=self.clear_all_services).pack(side="left", padx=(5, 0))

        services_wrap = tk.Frame(left, bg=PANEL)
        services_wrap.pack(fill="x", padx=10, pady=(0, 7))
        self.services_canvas = tk.Canvas(services_wrap, bg=PANEL, highlightthickness=0, bd=0, height=215)
        services_scroll = ttk.Scrollbar(services_wrap, orient="vertical", command=self.services_canvas.yview)
        self.services_canvas.configure(yscrollcommand=services_scroll.set)
        self.services_canvas.pack(side="left", fill="both", expand=True)
        services_scroll.pack(side="right", fill="y")
        self.services_inner = tk.Frame(self.services_canvas, bg=PANEL)
        self.services_window = self.services_canvas.create_window((0, 0), window=self.services_inner, anchor="nw")
        self.services_inner.bind("<Configure>", lambda _e: self.services_canvas.configure(
            scrollregion=self.services_canvas.bbox("all")))
        self.services_canvas.bind("<Configure>", lambda e: self.services_canvas.itemconfigure(
            self.services_window, width=e.width))
        self.services_canvas.bind("<MouseWheel>", lambda e: self.services_canvas.yview_scroll(
            int(-1 * (e.delta / 120)), "units"))
        for name, var in self.service_vars.items():
            checkbox = ttk.Checkbutton(self.services_inner, text=name, variable=var, command=self._save_state)
            checkbox.pack(anchor="w", padx=10, pady=2, fill="x")
            checkbox.bind("<MouseWheel>", lambda e: self.services_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        tk.Label(left, text="СВОИ ДОМЕНЫ", bg=PANEL, fg=FG, font=("Segoe UI Semibold", 10)).pack(
            anchor="w", padx=16, pady=(3, 4))
        self.custom_entry = ttk.Entry(left)
        self.custom_entry.pack(fill="x", padx=16)
        self.custom_entry.bind("<FocusOut>", lambda _e: self._save_state())
        tk.Label(left, text="Через запятую или пробел: service.example, api.example.com",
                 bg=PANEL, fg=MUTED, font=("Segoe UI", 8), wraplength=275, justify="left").pack(
            anchor="w", padx=16, pady=(4, 7))

        tk.Label(left, text="РЕЖИМ ПОДКЛЮЧЕНИЯ", bg=PANEL, fg=FG,
                 font=("Segoe UI Semibold", 10)).pack(anchor="w", padx=16, pady=(0, 4))
        self.mode_combo = ttk.Combobox(
            left, textvariable=self.mode_var,
            values=["Весь трафик (TUN)", "Только выбранные домены (TUN)", "Системный прокси (браузеры)"],
            state="readonly", width=31
        )
        self.mode_combo.pack(fill="x", padx=16)
        self.mode_combo.bind("<<ComboboxSelected>>", lambda _e: self._save_state())
        tk.Label(left, text="TUN охватывает обычные приложения. Для него Windows попросит права администратора. Системный прокси подходит только приложениям, которые его используют.",
                 bg=PANEL, fg=MUTED, font=("Segoe UI", 8), wraplength=275, justify="left").pack(
            anchor="w", padx=16, pady=(4, 7))

        ttk.Checkbutton(left, text="Включать системный прокси в браузерном режиме",
                        variable=self.use_system_proxy, command=self._save_state).pack(
            anchor="w", padx=16, pady=(0, 4))
        tk.Label(left, text="Локальный диагностический прокси: 127.0.0.1:2080",
                 bg=PANEL, fg=MUTED, font=("Consolas", 8), justify="left", wraplength=275).pack(
            anchor="w", padx=16, pady=(0, 10))

        tk.Label(right, text="ПРОФИЛЬ ПОДКЛЮЧЕНИЯ", bg=PANEL, fg=FG,
                 font=("Segoe UI Semibold", 12)).pack(anchor="w", padx=16, pady=(16, 4))
        tk.Label(right, textvariable=self.profile_var, bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9), anchor="w").pack(fill="x", padx=16, pady=(0, 10))

        tools = tk.Frame(right, bg=PANEL)
        tools.pack(fill="x", padx=16, pady=(0, 8))
        ttk.Button(tools, text="Импорт JSON", command=self.import_json).pack(side="left")
        ttk.Button(tools, text="Автоподбор узла", style="Accent.TButton", command=self.auto_find_node).pack(side="left", padx=(7, 0))
        ttk.Button(tools, text="Ещё", command=self.more_tools).pack(side="left", padx=(7, 0))

        editor_frame = tk.Frame(right, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
        editor_frame.pack(fill="both", expand=True, padx=16, pady=(0, 10))
        self.editor = tk.Text(editor_frame, height=12, wrap="word", bg=PANEL_2, fg=FG, insertbackground=FG,
                              relief="flat", borderwidth=0, font=("Consolas", 9), padx=10, pady=9,
                              selectbackground="#454b5a")
        scroll = ttk.Scrollbar(editor_frame, orient="vertical", command=self.editor.yview)
        self.editor.configure(yscrollcommand=scroll.set)
        self.editor.bind("<KeyPress>", self._manual_profile_edit)
        self.editor.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        tk.Label(right, text="Вставь одну ссылку VLESS / VMess / Trojan / Shadowsocks или полный sing-box JSON.",
                 bg=PANEL, fg=MUTED, font=("Segoe UI", 9), wraplength=650, justify="left").pack(
            anchor="w", padx=16, pady=(0, 12))

        controls = tk.Frame(right, bg=PANEL)
        controls.pack(fill="x", padx=16, pady=(0, 16))
        self.connect_btn = ttk.Button(controls, text="▶  Подключить", style="Accent.TButton", command=self.connect)
        self.connect_btn.pack(side="left")
        self.disconnect_btn = ttk.Button(controls, text="Отключить", command=self.disconnect, state="disabled")
        self.disconnect_btn.pack(side="left", padx=(8, 0))
        self.test_btn = ttk.Button(controls, text="Проверить интернет", command=self.test_connection, state="disabled")
        self.test_btn.pack(side="left", padx=(8, 0))
        ttk.Button(controls, text="Открыть папку логов", command=self.open_logs).pack(side="right")

        footer = tk.Frame(self.root, bg=BG)
        footer.pack(fill="x", padx=22, pady=(0, 14))
        tk.Label(footer, text="Поддерживает приложения, которые используют системный прокси. Не все приложения его учитывают.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(side="left")
        self.core_label = tk.Label(footer, text="sing-box: не установлен", bg=BG, fg=MUTED, font=("Segoe UI", 8))
        self.core_label.pack(side="right")

    def refresh_core_state(self):
        if CORE.exists():
            self.core_label.configure(text="sing-box: установлен", fg=GREEN)
        else:
            self.core_label.configure(text="sing-box: не установлен", fg=MUTED)

    def set_status(self, text, color=MUTED):
        self.status_var.set(text)
        self.status_pill.configure(fg=color)
        self.refresh_core_state()

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.root.after(0, lambda: self._append_log(f"[{timestamp}] {message}\n"))

    def _append_log(self, message):
        # Keep the UI log short; connection diagnostics are written to sing-box.log.
        print(message.rstrip())

    def import_json(self):
        path = filedialog.askopenfilename(title="Выбрать конфиг sing-box",
                                          filetypes=[("JSON config", "*.json"), ("All files", "*.*")])
        if not path:
            return
        try:
            text = Path(path).read_text(encoding="utf-8-sig")
            data = json.loads(text)
            if not isinstance(data, dict) or not isinstance(data.get("outbounds"), list):
                raise ValueError("В файле нет списка outbounds.")
            self.auto_profile_active = False
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", json.dumps(data, ensure_ascii=False, indent=2))
            self.loaded_path = path
            self.profile_var.set("Импортирован: " + Path(path).name)
        except Exception as exc:
            messagebox.showerror("Ошибка импорта", str(exc))

    def clear_input(self):
        self.auto_profile_active = False
        self.editor.delete("1.0", "end")
        self.loaded_path = ""
        self.profile_var.set("Профиль не загружен")

    def more_tools(self):
        menu = tk.Menu(self.root, tearoff=False, bg=PANEL_2, fg=FG, activebackground=ACCENT, activeforeground="white")
        menu.add_command(label="Выбрать sing-box.exe", command=self.import_core_file)
        menu.add_command(label="Скачать ядро вручную", command=self.install_core)
        menu.add_command(label="Очистить профиль", command=self.clear_input)
        try:
            menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            menu.grab_release()

    def auto_find_node(self):
        if self.busy:
            return
        if self.process and self.process.poll() is None:
            messagebox.showinfo("Сначала отключись", "Отключи текущее соединение перед автоматическим поиском нового узла.")
            return
        try:
            ensure_core_available()
            if not CORE.is_file():
                messagebox.showwarning("Ядро не найдено", "В этой сборке нет sing-box. Нажми «Ещё» → «Выбрать sing-box.exe» или скачай ядро вручную.")
                return
        except Exception as exc:
            messagebox.showerror("Ошибка", str(exc))
            return
        selected = [name for name, var in self.service_vars.items() if var.get()]
        custom_domains = self.custom_entry.get().strip()
        if not selected and not custom_domains:
            messagebox.showwarning("Нет правил", "Выбери хотя бы один сервис или введи свои домены.")
            return
        self.busy = True
        self.connect_btn.configure(state="disabled")
        self.set_status("Ищу и проверяю узлы…", "#ffcf70")
        threading.Thread(target=self._auto_find_worker, args=(selected, custom_domains), daemon=True).start()

    def _probe_auto_candidate(self, candidate, selected, custom_domains, port):
        """Validate a full sing-box pool or one URI through a temporary local mixed inbound."""
        config_path = APP_DIR / f"auto-probe-{port}.json"
        log_path = APP_DIR / f"auto-probe-{port}.log"
        process = None
        log_handle = None
        try:
            data, _ = parse_uri(candidate)
            config = make_probe_config(data, selected, custom_domains, inbound_port=port)
            config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
            check = subprocess.run(
                [str(CORE), "check", "-c", str(config_path)],
                capture_output=True, text=True, timeout=12,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
            )
            if check.returncode != 0:
                detail = (check.stderr or check.stdout or "config check failed").strip()[-900:]
                return False, "sing-box rejected candidate: " + detail
            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write("\n--- auto-probe " + time.strftime("%Y-%m-%d %H:%M:%S") + " ---\n")
            log_handle = open(log_path, "a", encoding="utf-8")
            process = subprocess.Popen(
                [str(CORE), "run", "-c", str(config_path)],
                stdout=log_handle, stderr=subprocess.STDOUT,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
            )
            log_handle.close()
            log_handle = None

            ready = False
            for _ in range(24):
                if process.poll() is not None:
                    try:
                        detail = "\n".join(log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-8:])
                    except Exception:
                        detail = ""
                    return False, "sing-box exited: " + detail[-700:]
                try:
                    with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                        ready = True
                        break
                except OSError:
                    time.sleep(0.12)
            if not ready:
                return False, "local inbound didn't start"

            proxies = {"http": f"http://127.0.0.1:{port}", "https": f"http://127.0.0.1:{port}"}
            opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxies))
            probe_errors = []
            # 204 is the primary probe; example.com is only a fallback in case the first endpoint is filtered.
            for target in ("https://cp.cloudflare.com/generate_204", "https://example.com/", "https://www.gstatic.com/generate_204", "https://www.microsoft.com/"):
                try:
                    req = urllib.request.Request(target, headers={"User-Agent": "CheburekAccess/2.1"})
                    with opener.open(req, timeout=4.5) as response:
                        if 200 <= response.status < 400:
                            return True, target
                        probe_errors.append(f"{target}: HTTP {response.status}")
                except Exception as exc:
                    probe_errors.append(f"{target}: {exc}")
            return False, "; ".join(probe_errors[-2:])
        except Exception as exc:
            return False, str(exc)
        finally:
            if log_handle:
                try:
                    log_handle.close()
                except Exception:
                    pass
            if process is not None:
                try:
                    if process.poll() is None:
                        process.terminate()
                        try:
                            process.wait(timeout=2)
                        except subprocess.TimeoutExpired:
                            process.kill()
                except Exception:
                    pass

    def _auto_find_worker(self, selected, custom_domains):
        errors = []
        profile_candidates = []
        uri_candidates = []
        sources_ok = 0

        # First try a complete, recently regenerated sing-box profile. Its urltest outbound
        # can fail over between its own nodes; this avoids betting everything on 24 stale links.
        for source in PUBLIC_PROFILE_FEEDS:
            try:
                request = urllib.request.Request(
                    source, headers={"User-Agent": "CheburekAccess/2.1", "Accept": "application/json,text/plain,*/*"}
                )
                with urllib.request.urlopen(request, timeout=14) as response:
                    raw_bytes = response.read(MAX_FEED_BYTES + 1)
                if len(raw_bytes) > MAX_FEED_BYTES:
                    errors.append(f"{urllib.parse.urlparse(source).netloc}: feed exceeds {MAX_FEED_BYTES // 1_000_000} MB")
                    continue
                body = raw_bytes.decode("utf-8-sig", "replace").strip()
                if not body.startswith("{"):
                    errors.append(f"{urllib.parse.urlparse(source).netloc}: response was not JSON")
                    continue
                profile = json.loads(body)
                if not isinstance(profile, dict) or not isinstance(profile.get("outbounds"), list) or not profile["outbounds"]:
                    errors.append(f"{urllib.parse.urlparse(source).netloc}: no outbounds in JSON")
                    continue
                profile_candidates.append(json.dumps(profile, ensure_ascii=False))
                sources_ok += 1
                break
            except Exception as exc:
                errors.append(f"{urllib.parse.urlparse(source).netloc}: {exc}")

        for source in PUBLIC_NODE_FEEDS:
            try:
                request = urllib.request.Request(
                    source, headers={"User-Agent": "CheburekAccess/2.1", "Accept": "text/plain,*/*"}
                )
                with urllib.request.urlopen(request, timeout=14) as response:
                    raw_bytes = response.read(MAX_FEED_BYTES + 1)
                if len(raw_bytes) > MAX_FEED_BYTES:
                    errors.append(f"{urllib.parse.urlparse(source).netloc}: feed is too large")
                    continue
                body = raw_bytes.decode("utf-8-sig", "replace")
                extracted = extract_profile_candidates(body)
                sources_ok += 1
                # Keep a small set of full JSON profiles at the front and collect links from more
                # than one source; do not stop after the first 18 candidates.
                for item in extracted:
                    if item.lstrip().startswith("{"):
                        if item not in profile_candidates:
                            profile_candidates.append(item)
                    elif item not in uri_candidates:
                        uri_candidates.append(item)
                if len(uri_candidates) >= 5000:
                    break
            except Exception as exc:
                errors.append(f"{urllib.parse.urlparse(source).netloc}: {exc}")

        # Dedupe large pool profiles separately from individual links.
        profile_candidates = list(dict.fromkeys(profile_candidates))[:3]
        if not profile_candidates and not uri_candidates:
            detail = "\n".join(errors[-5:]) or "No JSON profiles or supported proxy links were found."
            self.root.after(0, lambda e=detail: self._auto_find_failed(
                "Не удалось скачать рабочие источники профилей. Проверь интернет-доступ к зеркалам и попробуй ещё раз.\n\n" + e
            ))
            return

        # Try complete auto/urltest pools first, serially: they can select a valid node internally.
        checked = 0
        failures = []
        for profile_index, profile in enumerate(profile_candidates, 1):
            self.root.after(0, lambda i=profile_index, n=len(profile_candidates): self.set_status(
                f"Проверяю готовый пул узлов {i}/{n}…", "#ffcf70"
            ))
            ok, detail = self._probe_auto_candidate(profile, selected, custom_domains, MIXED_PORT)
            checked += 1
            if ok:
                self.root.after(0, lambda p=profile, i=profile_index, n=len(profile_candidates):
                                self._auto_find_success(p, i, n, "JSON-пул"))
                return
            failures.append("JSON profile: " + detail)

        # The text feeds can include thousands of links. Test a wider batch in parallel on distinct
        # local ports so dead links don't cause a multi-minute sequential wait.
        candidate_limit = min(180, len(uri_candidates))
        if len(uri_candidates) > candidate_limit:
            # Spread the test across the whole feed. The first rows are often stale or
            # clustered by provider; repeated runs rotate the subset rather than retrying them.
            candidates = random.Random(time.time_ns()).sample(uri_candidates, candidate_limit)
        else:
            candidates = uri_candidates[:]
        if candidates:
            self.root.after(0, lambda n=candidate_limit: self.set_status(
                f"Проверяю {n} отдельных узлов…", "#ffcf70"
            ))
        found = None
        found_index = 0
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_map = {}
            for index, candidate in enumerate(candidates, 1):
                port = 21000 + index
                future = executor.submit(self._probe_auto_candidate, candidate, selected, custom_domains, port)
                future_map[future] = (index, candidate)
            for future in as_completed(future_map):
                index, candidate = future_map[future]
                try:
                    ok, detail = future.result()
                except Exception as exc:
                    ok, detail = False, str(exc)
                checked += 1
                if ok:
                    found, found_index = candidate, index
                    # We cannot safely kill futures already running, but will cancel queued ones.
                    for other in future_map:
                        if other is not future:
                            other.cancel()
                    break
                if detail:
                    failures.append(f"node {index}: {detail}")
                if checked % 5 == 0:
                    self.root.after(0, lambda c=checked, t=candidate_limit + len(profile_candidates):
                                    self.set_status(f"Проверено {c}/{t} профилей…", "#ffcf70"))

        if found is not None:
            self.root.after(0, lambda u=found, i=found_index, t=candidate_limit:
                            self._auto_find_success(u, i, t, "отдельный узел"))
            return

        details = errors[-3:] + failures[-3:]
        detail = "\n".join(details) or "Все загруженные профили и узлы не прошли HTTPS-проверку."
        reason = (
            f"Загружено источников: {sources_ok}; проверено профилей/узлов: {checked}.\n"
            "Не нашлось узла, который смог пройти HTTPS через локальный прокси. "
            "Часть общедоступных узлов может быть недоступна именно у твоего провайдера.\n\n"
            + detail
        )
        self.root.after(0, lambda e=reason: self._auto_find_failed(reason))

    def _auto_find_success(self, candidate, index, total, candidate_kind="отдельный узел"):
        self.busy = False
        self.connect_btn.configure(state="normal")
        self.auto_profile_active = candidate.lstrip().startswith("{")
        if self.auto_profile_active:
            # A full subscription can be megabytes. Keep it in AppData instead of freezing the text widget.
            AUTO_PROFILE_PATH.write_text(candidate, encoding="utf-8")
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", "Автоматический профиль sing-box\nПул узлов сохранён локально. Нажми «Подключиться», чтобы использовать его.")
            self.loaded_path = "public-auto-discovery-json"
            self.profile_var.set(f"Проверен автоматический пул узлов • источник {index}/{total}")
        else:
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", candidate)
            self.loaded_path = "public-auto-discovery"
            self.profile_var.set(f"Проверен публичный узел • кандидат {index}/{total}")
        self.set_status("Узел найден", GREEN)
        self._save_state()
        messagebox.showinfo(
            "Узел найден",
            f"Профиль прошёл HTTPS-проверку через твою сеть ({candidate_kind}). Сейчас запускаю подключение.\n\n"
            "Публичные сторонние узлы нестабильны и не подходят для важных аккаунтов."
        )
        self.root.after(150, self.connect)

    def _auto_find_failed(self, error):
        self.busy = False
        self.connect_btn.configure(state="normal")
        self.set_status("Рабочий узел не найден", ACCENT)
        messagebox.showerror("Автоподбор не удался", error + "\n\nЕсли зеркала подписок недоступны из твоей сети, этот режим не сможет загрузить список. Не вводи пароль от чувствительных аккаунтов через публичные узлы.")

    def import_core_file(self):
        path = filedialog.askopenfilename(
            title="Выбрать sing-box.exe",
            filetypes=[("sing-box executable", "sing-box.exe"), ("Executable files", "*.exe"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            result = subprocess.run([path, "version"], capture_output=True, text=True, timeout=10,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            output = (result.stdout or result.stderr or "").strip()
            if result.returncode != 0 or "sing-box" not in output.lower():
                raise ValueError("Выбранный файл не прошёл проверку команды 'sing-box version'.")
            ensure_app_dir()
            shutil.copy2(path, CORE)
            self.set_status("Ядро импортировано", GREEN)
            self.profile_var.set("Ядро импортировано: " + Path(path).name)
            messagebox.showinfo("Готово", "sing-box установлен локально. Для этой операции доступ к GitHub не нужен.")
        except Exception as exc:
            messagebox.showerror("Не удалось импортировать ядро", str(exc))

    def install_core(self):
        if self.busy:
            return
        # A self-contained build ships with the official sing-box binary.
        # Never attempt a network download when the core is already available locally.
        try:
            ensure_app_dir()
            if CORE.is_file():
                self.set_status("Ядро уже установлено", GREEN)
                self.profile_var.set("sing-box доступен локально • можно подключаться")
                messagebox.showinfo("Ядро готово", "sing-box уже установлен. Скачивать его заново не нужно — вставь профиль и нажми «Подключить».")
                return
            if BUNDLED_CORE.is_file():
                shutil.copy2(BUNDLED_CORE, CORE)
                self.set_status("Ядро установлено", GREEN)
                self.profile_var.set("sing-box извлечён из EXE • можно подключаться")
                messagebox.showinfo("Готово", "sing-box извлечён из EXE. Доступ к GitHub не требуется.")
                return
        except Exception as exc:
            messagebox.showerror("Ошибка локальной установки", str(exc))
            return
        self.busy = True
        self.set_status("Загрузка ядра…", "#ffcf70")
        self.connect_btn.configure(state="disabled")
        threading.Thread(target=self._install_core_worker, daemon=True).start()

    def _install_core_worker(self):
        try:
            ensure_app_dir()
            api = "https://api.github.com/repos/SagerNet/sing-box/releases/latest"
            request = urllib.request.Request(api, headers={"User-Agent": "CheburekAccess/1.0", "Accept": "application/vnd.github+json"})
            with urllib.request.urlopen(request, timeout=30) as response:
                release = json.loads(response.read().decode("utf-8"))
            candidates = [a for a in release.get("assets", []) if a.get("name", "").endswith("windows-amd64.zip")]
            if not candidates:
                raise RuntimeError("В последнем стабильном релизе не найден архив Windows amd64.")
            asset = candidates[0]
            req = urllib.request.Request(asset["browser_download_url"], headers={"User-Agent": "CheburekAccess/1.0"})
            with urllib.request.urlopen(req, timeout=120) as response:
                archive = response.read()
            digest = asset.get("digest", "")
            if digest.startswith("sha256:"):
                actual = hashlib.sha256(archive).hexdigest()
                if actual.lower() != digest.split(":", 1)[1].lower():
                    raise RuntimeError("SHA-256 скачанного архива не совпал с официальным digest GitHub.")
            tmp = APP_DIR / "sing-box.zip"
            tmp.write_bytes(archive)
            exe_data = None
            with zipfile.ZipFile(tmp) as zf:
                names = [n for n in zf.namelist() if n.lower().endswith("sing-box.exe") and not n.endswith("/")]
                if not names:
                    raise RuntimeError("В архиве не найден sing-box.exe.")
                exe_data = zf.read(names[0])
            tmp.unlink(missing_ok=True)
            CORE.write_bytes(exe_data)
            self.root.after(0, lambda: self._core_installed(release.get("tag_name", "latest")))
        except Exception as exc:
            err = str(exc)
            self.root.after(0, lambda e=err: self._core_failed(e))

    def _core_installed(self, version):
        self.busy = False
        self.connect_btn.configure(state="normal")
        self.set_status("Ядро установлено", GREEN)
        self.profile_var.set(f"sing-box {version} • можно подключаться")
        messagebox.showinfo("Готово", f"Официальное ядро sing-box {version} скачано и проверено по SHA-256.")
    def _core_failed(self, error):
        self.busy = False
        self.connect_btn.configure(state="normal")
        self.set_status("Не удалось скачать ядро", ACCENT)
        messagebox.showerror(
            "Ошибка установки",
            error + "\n\nНовая версия Cheburek включает sing-box внутри EXE. Если ты видишь это окно, используй обновлённую сборку; либо скачай sing-box с официальной страницы https://github.com/SagerNet/sing-box/releases, распакуй архив и нажми «Выбрать sing-box.exe»."
        )

    def connect(self):
        if self.busy or self.process:
            return
        if not CORE.exists():
            messagebox.showinfo("Нужно ядро", "Встроенное ядро не найдено. Открой «Ещё» и выбери sing-box.exe.")
            return
        mode = self.mode_var.get()
        if mode in ("Весь трафик (TUN)", "Только выбранные домены (TUN)") and not is_admin():
            if messagebox.askyesno(
                "Нужны права администратора",
                "Режим TUN маршрутизирует трафик всех приложений и требует разрешения Windows на создание сетевого интерфейса. Перезапустить Cheburek от имени администратора?"
            ):
                self.restart_as_admin()
            return
        raw = AUTO_PROFILE_TOKEN if getattr(self, "auto_profile_active", False) else self.editor.get("1.0", "end").strip()
        selected = [name for name, var in self.service_vars.items() if var.get()]
        custom_domains = self.custom_entry.get().strip()
        if not selected and not custom_domains and mode != "Весь трафик (TUN)":
            messagebox.showwarning("Нет правил", "Выбери категорию доменов или введи свои домены. В режиме «Весь трафик» список категорий не обязателен.")
            return
        self._save_state()
        self.busy = True
        self.connect_btn.configure(state="disabled")
        self.set_status("Проверка профиля…", "#ffcf70")
        use_system_proxy = self.use_system_proxy.get()
        threading.Thread(target=self._connect_worker, args=(raw, selected, custom_domains, mode, use_system_proxy), daemon=True).start()

    def _probe_running_proxy(self):
        proxies = {
            "http": f"http://127.0.0.1:{MIXED_PORT}",
            "https": f"http://127.0.0.1:{MIXED_PORT}",
        }
        opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxies))
        errors = []
        targets = (
            "https://cp.cloudflare.com/generate_204",
            "https://example.com/",
            "https://www.gstatic.com/generate_204",
            "https://www.microsoft.com/",
            "https://www.google.com/generate_204",
        )
        for target in targets:
            try:
                request = urllib.request.Request(target, headers={"User-Agent": "CheburekAccess/2.0"})
                with opener.open(request, timeout=8) as response:
                    if 200 <= response.status < 400:
                        return target
                    errors.append(f"{target}: HTTP {response.status}")
            except Exception as exc:
                errors.append(f"{target}: {exc}")
        raise RuntimeError(
            "Локальный прокси запустился, но ни одна HTTPS-проверка не прошла через внешний узел. "
            "Сервер может быть отключён, не поддерживать этот трафик или блокировать тестовые сайты.\n\n"
            + "\n".join(errors[-3:])
            + "\n\nПопробуй «Автоподбор узла» или другой профиль. Программа не будет отмечать соединение успешным без этой проверки."
        )

    def test_connection(self):
        if not self.process or self.process.poll() is not None:
            messagebox.showinfo("Нет подключения", "Сначала подключись к узлу.")
            return
        self.set_status("Проверяю внешний узел…", "#ffcf70")
        self.test_btn.configure(state="disabled")
        threading.Thread(target=self._test_connection_worker, daemon=True).start()

    def _test_connection_worker(self):
        try:
            target = self._probe_running_proxy()
            self.root.after(0, lambda t=target: self._test_connection_done(t, None))
        except Exception as exc:
            error = str(exc)
            self.root.after(0, lambda e=error: self._test_connection_done(None, e))

    def _test_connection_done(self, target, error):
        self.test_btn.configure(state="normal")
        if error:
            self.set_status("Проверка не прошла", ACCENT)
            messagebox.showerror("Проверка соединения", error)
        else:
            self.set_status("Подключено • HTTPS OK", GREEN)
            messagebox.showinfo("Проверка успешна", f"Внешний узел ответил через прокси:\n{target}")

    def _connect_worker(self, raw, selected, custom_domains, mode, use_system_proxy):
        try:
            if raw == AUTO_PROFILE_TOKEN:
                if not AUTO_PROFILE_PATH.is_file():
                    raise ValueError("Автоматический JSON-профиль не найден. Нажми «Автоподбор узла» ещё раз.")
                data = json.loads(AUTO_PROFILE_PATH.read_text(encoding="utf-8"))
                already_json = True
            else:
                data, already_json = parse_uri(raw)
            config = make_routing_config(data, selected, custom_domains, mode)
            CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
            check = subprocess.run([str(CORE), "check", "-c", str(CONFIG_PATH)],
                                   capture_output=True, text=True, timeout=30,
                                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            if check.returncode != 0:
                detail = (check.stderr or check.stdout or "sing-box check не прошёл").strip()
                raise RuntimeError("sing-box отклонил профиль:\n" + detail[-2200:])
            with open(LOG_PATH, "a", encoding="utf-8") as log_file:
                log_file.write("\n--- Cheburek start " + time.strftime("%Y-%m-%d %H:%M:%S") + f" mode={mode} ---\n")
            log_file = open(LOG_PATH, "a", encoding="utf-8")
            self.process = subprocess.Popen([str(CORE), "run", "-c", str(CONFIG_PATH)],
                                            stdout=log_file, stderr=subprocess.STDOUT,
                                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            log_file.close()
            ready = False
            for _ in range(50):
                if self.process.poll() is not None:
                    detail = ""
                    try:
                        detail = "\n".join(LOG_PATH.read_text(encoding="utf-8", errors="replace").splitlines()[-18:])
                    except Exception:
                        pass
                    raise RuntimeError("sing-box завершился сразу после запуска.\n\n" + detail[-1800:])
                try:
                    with socket.create_connection(("127.0.0.1", MIXED_PORT), timeout=0.3):
                        ready = True
                        break
                except OSError:
                    time.sleep(0.2)
            if not ready:
                raise RuntimeError("Локальный прокси не открыл порт 2080 за 10 секунд. Открой папку логов.")
            # Do not report success until an external HTTPS request has passed through the selected outbound.
            tested_target = self._probe_running_proxy()
            if mode == "Системный прокси (браузеры)" and use_system_proxy:
                self._enable_system_proxy()
            self.root.after(0, lambda m=mode, target=tested_target: self._connected(m, target))
        except Exception as exc:
            self._stop_process_silent()
            err = str(exc)
            self.root.after(0, lambda e=err: self._connect_failed(e))

    def _connected(self, mode, tested_target):
        self.busy = False
        self.connect_btn.configure(state="disabled")
        self.disconnect_btn.configure(state="normal")
        self.test_btn.configure(state="normal")
        self.set_status("Подключено • HTTPS OK", GREEN)
        self.profile_var.set(f"Узел отвечает • проверка: {urllib.parse.urlparse(tested_target).netloc}")
        if mode == "Весь трафик (TUN)":
            detail = "TUN включён: внешний трафик приложений направляется через прокси. Локальные сети оставлены доступными."
        elif mode == "Только выбранные домены (TUN)":
            detail = "TUN включён: домены выбранных категорий маршрутизируются через прокси, остальные соединения идут напрямую."
        elif self.use_system_proxy.get():
            detail = "Системный прокси Windows включён: приложения, которые используют настройки Windows, смогут работать через выбранные домены."
        else:
            detail = "Прокси работает на 127.0.0.1:2080. Системный прокси Windows выключен; настрой его в приложении или включи соответствующий флажок."
        messagebox.showinfo("Подключено", detail + f"\n\nВнешняя HTTPS-проверка прошла через узел: {urllib.parse.urlparse(tested_target).netloc}")

    def _connect_failed(self, error):
        self.busy = False
        self.connect_btn.configure(state="normal")
        self.disconnect_btn.configure(state="disabled")
        self.test_btn.configure(state="disabled")
        self.set_status("Ошибка подключения", ACCENT)
        messagebox.showerror("Не удалось подключиться", error)

    def _stop_process_silent(self):
        try:
            if self.process and self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.process.kill()
        except Exception:
            pass
        self.process = None

    def disconnect(self):
        self._stop_process_silent()
        if self.proxy_changed:
            try:
                if BACKUP_PATH.exists():
                    write_registry_values(json.loads(BACKUP_PATH.read_text(encoding="utf-8")))
                    BACKUP_PATH.unlink(missing_ok=True)
            except Exception as exc:
                messagebox.showwarning("Прокси Windows", "Не удалось восстановить прежние настройки прокси:\n" + str(exc))
            self.proxy_changed = False
        self.connect_btn.configure(state="normal")
        self.disconnect_btn.configure(state="disabled")
        self.test_btn.configure(state="disabled")
        self.set_status("Отключено", MUTED)
        self.profile_var.set("Подключение остановлено")
        self._save_state()

    def open_logs(self):
        ensure_app_dir()
        target = APP_DIR
        try:
            os.startfile(str(target))
        except Exception:
            messagebox.showinfo("Папка приложения", str(target))

    def on_close(self):
        self._save_state()
        self.disconnect()
        self.root.destroy()


def main():
    root = tk.Tk()
    CheburekApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
