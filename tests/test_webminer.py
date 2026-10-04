import unittest

from WebMiner import is_valid_url


class WebMinerTests(unittest.TestCase):
    def test_valid_https_url(self):
        self.assertTrue(is_valid_url("https://example.com/path"))

    def test_valid_http_url(self):
        self.assertTrue(is_valid_url("http://example.com"))

    def test_missing_scheme(self):
        self.assertFalse(is_valid_url("example.com"))

    def test_invalid_text(self):
        self.assertFalse(is_valid_url("not a url"))


if __name__ == "__main__":
    unittest.main()