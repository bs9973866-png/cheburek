import unittest

from app import extract_proxy_uris, make_probe_config, make_routing_config, parse_uri


class ProfileTests(unittest.TestCase):
    def test_extract_plain_subscription_uris(self):
        body = "# tested profiles\nvless://uuid@example.org:443?security=tls\nhttps://example.org/not-a-node\n"
        nodes = extract_proxy_uris(body)
        self.assertEqual(len(nodes), 1)
        self.assertTrue(nodes[0].startswith("vless://"))

    def test_extract_base64_subscription_uris(self):
        import base64
        raw = "vless://uuid@example.org:443?security=tls\ntrojan://secret@example.org:443\n"
        encoded = base64.b64encode(raw.encode()).decode()
        self.assertEqual(len(extract_proxy_uris(encoded)), 2)

    def test_vless_uri_creates_tls_proxy(self):
        config, imported = parse_uri(
            "vless://11111111-1111-4111-8111-111111111111@example.org:443"
            "?security=tls&sni=cdn.example.org&type=ws&path=%2Fedge&host=cdn.example.org"
        )
        self.assertFalse(imported)
        outbound = config["outbounds"][0]
        self.assertEqual(outbound["type"], "vless")
        self.assertEqual(outbound["tls"]["server_name"], "cdn.example.org")
        self.assertEqual(outbound["transport"]["type"], "ws")

    def test_trojan_uri(self):
        config, imported = parse_uri("trojan://secret@example.org:443?sni=example.org")
        self.assertFalse(imported)
        self.assertEqual(config["outbounds"][0]["type"], "trojan")
        self.assertEqual(config["outbounds"][0]["password"], "secret")

    def test_imported_config_adds_split_routes(self):
        source = {
            "outbounds": [
                {"type": "vless", "tag": "primary", "server": "proxy.example", "server_port": 443,
                 "uuid": "11111111-1111-4111-8111-111111111111"},
                {"type": "direct", "tag": "direct"}
            ],
            "inbounds": [],
            "route": {"rules": []}
        }
        config, imported = parse_uri(__import__("json").dumps(source))
        self.assertTrue(imported)
        ready = make_routing_config(
            config, ["OpenAI / Codex", "YouTube"], "example.net",
            "Только выбранные домены (TUN)"
        )
        self.assertEqual(ready["route"]["final"], "direct")
        self.assertEqual(ready["inbounds"][0]["type"], "tun")
        self.assertEqual(ready["inbounds"][1]["type"], "mixed")
        self.assertTrue(any(rule.get("action") == "sniff" for rule in ready["route"]["rules"]))
        proxy_rules = [rule for rule in ready["route"]["rules"] if rule.get("outbound") == "primary"]
        self.assertTrue(any("youtube.com" in rule.get("domain_suffix", []) for rule in proxy_rules))
        self.assertTrue(any("example.net" in rule.get("domain_suffix", []) for rule in proxy_rules))

    def test_full_tunnel_sends_all_non_lan_traffic_to_proxy(self):
        source = {
            "outbounds": [
                {"type": "vless", "tag": "main-proxy", "server": "proxy.example", "server_port": 443,
                 "uuid": "11111111-1111-4111-8111-111111111111"},
                {"type": "direct", "tag": "direct"}
            ],
            "inbounds": [],
            "route": {"rules": []}
        }
        ready = make_routing_config(source, [], "", "Весь трафик (TUN)")
        self.assertEqual(ready["route"]["final"], "main-proxy")
        self.assertEqual(ready["inbounds"][0]["type"], "tun")
        self.assertTrue(any(rule.get("ip_is_private") for rule in ready["route"]["rules"]))

    def test_service_catalog_has_large_deduplicated_domain_coverage(self):
        from app import SERVICES
        domains = [d for values in SERVICES.values() for d in values]
        self.assertGreaterEqual(len(set(domains)), 250)
        self.assertTrue(any("web.whatsapp.com" in values for values in SERVICES.values()))
        self.assertTrue(any("telegram.org" in values for values in SERVICES.values()))

    def test_auto_discovery_probe_routes_through_selected_proxy(self):
        source = {
            "outbounds": [
                {"type": "vless", "tag": "main-proxy", "server": "proxy.example", "server_port": 443,
                 "uuid": "11111111-1111-4111-8111-111111111111"},
                {"type": "direct", "tag": "direct"}
            ],
            "inbounds": [],
            "route": {"rules": []}
        }
        config = make_probe_config(source, ["OpenAI / Codex"], "")
        first_rule = config["route"]["rules"][0]
        self.assertEqual(first_rule["outbound"], "main-proxy")
        self.assertIn("cp.cloudflare.com", first_rule["domain_suffix"])
        self.assertIn("example.com", first_rule["domain_suffix"])

    def test_invalid_custom_domain_rejected(self):
        source = {"outbounds": [{"type": "vless", "tag": "proxy"}], "inbounds": []}
        with self.assertRaises(ValueError):
            make_routing_config(source, [], "bad_domain.com")


if __name__ == "__main__":
    unittest.main()
