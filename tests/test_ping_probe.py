import unittest

from src.ping_probe import parse_latency_ms


class TestParseLatencyMs(unittest.TestCase):
    def test_parse_linux_output(self):
        output = "64 bytes from 8.8.8.8: icmp_seq=1 ttl=117 time=23.4 ms"
        self.assertEqual(parse_latency_ms(output), 23.4)

    def test_parse_windows_output(self):
        output = "Reply from 8.8.8.8: bytes=32 time=17ms TTL=117"
        self.assertEqual(parse_latency_ms(output), 17.0)

    def test_parse_russian_output(self):
        output = "Ответ от 1.1.1.1: число байт=32 время=42мс TTL=57"
        self.assertEqual(parse_latency_ms(output), 42.0)

    def test_return_none_when_latency_missing(self):
        output = "Request timed out"
        self.assertIsNone(parse_latency_ms(output))


if __name__ == "__main__":
    unittest.main()
