import unittest

from app import make_routing_config, parse_uri


class ProfileTests(unittest.TestCase):
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
        ready = make_routing_config(config, ["OpenAI / Codex", "YouTube"], "example.net")
        self.assertEqual(ready["route"]["final"], "direct")
        self.assertEqual(ready["inbounds"][0]["type"], "mixed")
        self.assertEqual(ready["route"]["rules"][0]["outbound"], "primary")
        self.assertIn("youtube.com", ready["route"]["rules"][1]["domain_suffix"])
        self.assertIn("example.net", ready["route"]["rules"][2]["domain_suffix"])

    def test_invalid_custom_domain_rejected(self):
        source = {"outbounds": [{"type": "vless", "tag": "proxy"}], "inbounds": []}
        with self.assertRaises(ValueError):
            make_routing_config(source, [], "bad_domain.com")


if __name__ == "__main__":
    unittest.main()
