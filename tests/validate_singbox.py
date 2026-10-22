import json
import subprocess
import sys
import tempfile
from pathlib import Path

from app import make_routing_config


def main():
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python tests/validate_singbox.py path/to/sing-box.exe')
    core = str(Path(sys.argv[1]).resolve())
    source = {
        'outbounds': [
            {'type': 'vless', 'tag': 'test-proxy', 'server': 'example.com', 'server_port': 443,
             'uuid': '11111111-1111-4111-8111-111111111111',
             'tls': {'enabled': True, 'server_name': 'example.com'}},
            {'type': 'direct', 'tag': 'direct'}
        ],
        'inbounds': [],
        'route': {'rules': []}
    }
    modes = [
        'Весь трафик (TUN)',
        'Только выбранные домены (TUN)',
        'Системный прокси (браузеры)'
    ]
    with tempfile.TemporaryDirectory() as temp:
        for index, mode in enumerate(modes):
            config = make_routing_config(source, ['OpenAI / Codex', 'Telegram', 'WhatsApp', 'YouTube'], 'example.net', mode)
            path = Path(temp) / f'config-{index}.json'
            path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')
            result = subprocess.run([core, 'check', '-c', str(path)], capture_output=True, text=True, timeout=30)
            if result.returncode:
                raise SystemExit(f'Config validation failed for mode {mode}:\n{result.stderr}\n{result.stdout}')
            print(f'OK: {mode}')


if __name__ == '__main__':
    main()
