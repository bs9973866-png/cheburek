import json
import random
import sys
from pathlib import Path

ALLOWED_TYPES = {'hysteria2', 'vless', 'trojan', 'shadowsocks', 'vmess', 'tuic'}
BAD_TRANSPORTS = {'xhttp', 'splithttp'}
PER_TYPE = {'hysteria2': 28, 'vless': 32, 'trojan': 28, 'shadowsocks': 18, 'vmess': 18, 'tuic': 6}

def main():
    if len(sys.argv) != 3:
        raise SystemExit('Usage: build_profile.py input-singbox.json output-profile.json')
    source = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
    source_outbounds = source.get('outbounds', [])
    source_endpoints = source.get('endpoints', [])
    if not source_outbounds:
        raise SystemExit('Source has no outbounds')
    rng = random.SystemRandom()
    chosen = []
    seen_servers = set()
    for node_type, limit in PER_TYPE.items():
        pool = []
        for ob in source_outbounds:
            if ob.get('type') != node_type or not ob.get('tag'):
                continue
            if not ob.get('server') or not ob.get('server_port'):
                continue
            transport_type = (ob.get('transport') or {}).get('type', '')
            if transport_type.lower() in BAD_TRANSPORTS:
                continue
            tls = ob.get('tls') or {}
            if tls.get('reality', {}).get('enabled') and not tls.get('server_name'):
                continue
            key = (node_type, str(ob.get('server')).lower(), int(ob.get('server_port')))
            if key in seen_servers:
                continue
            seen_servers.add(key)
            pool.append(ob)
        rng.shuffle(pool)
        chosen.extend(pool[:limit])
    if len(chosen) < 20:
        raise SystemExit(f'Not enough compatible node outbounds: {len(chosen)}')
    endpoints = []
    for ep in source_endpoints:
        if ep.get('type') == 'wireguard' and ep.get('tag') and ep.get('peers') and ep.get('private_key'):
            endpoints.append(ep)
    rng.shuffle(endpoints)
    endpoints = endpoints[:18]
    tags = [ob['tag'] for ob in chosen] + [ep['tag'] for ep in endpoints]
    if not tags:
        raise SystemExit('No selectable nodes found')
    outbounds = list(chosen)
    outbounds.extend(endpoints and [] or [])
    outbounds.extend([
        {
            'type': 'urltest', 'tag': 'auto', 'outbounds': tags,
            'url': 'https://www.gstatic.com/generate_204', 'interval': '3m',
            'tolerance': 80, 'interrupt_exist_connections': True
        },
        {'type': 'selector', 'tag': 'select', 'outbounds': ['auto'] + tags, 'default': 'auto'},
        {'type': 'direct', 'tag': 'direct'}
    ])
    profile = {
        'log': {'level': 'warn'},
        'endpoints': endpoints,
        'outbounds': outbounds,
        'route': {'final': 'auto', 'auto_detect_interface': True}
    }
    out_path = Path(sys.argv[2])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    summary = {
        'outbounds': len(outbounds), 'individual_nodes': len(chosen), 'wireguard_endpoints': len(endpoints),
        'types': {t: sum(1 for ob in chosen if ob.get('type') == t) for t in PER_TYPE}
    }
    print(json.dumps(summary))

if __name__ == '__main__':
    main()
