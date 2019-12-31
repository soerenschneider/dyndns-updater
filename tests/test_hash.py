from unittest import TestCase

from notifier import UpdateNotifier

class TestHash(TestCase):
    def test_hash(self):
        expected_hash = "1a83e3f81b8da3ddde19426f7bf439c8733792964fb02962c21a08d80d963d75"
        hashed = UpdateNotifier.hash_request(host="host",shared_secret="secret",external_ip="8.8.8.8")
        self.assertEqual(expected_hash, hashed)

    def test_hash_missing_host(self):
        with self.assertRaises(ValueError):
            UpdateNotifier.hash_request(host="",shared_secret="secret",external_ip="8.8.8.8")

    def test_hash_missing_ip(self):
        with self.assertRaises(ValueError):
            UpdateNotifier.hash_request(host="host",shared_secret="secret",external_ip="")

    def test_hash_missing_secret(self):
        with self.assertRaises(ValueError):
            UpdateNotifier.hash_request(host="host",shared_secret="",external_ip="8.8.8.8")
    