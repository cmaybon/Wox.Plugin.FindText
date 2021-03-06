import unittest
from unittest import TestCase

from find_text import FindText


class TestMain(TestCase):
    def setUp(self):
        self.ocr_result = {
            "text": [
                "we",
                "oreo",
                "ow",
                "=",
                "Getting",
                "the",
                "bounding",
                "box",
                "of",
                "the",
                "recognized",
                "words",
                "",
                "=",
                "",
                "s",
                "|",
                "getting",
                "tHE",
                "bOUndING",
                "screen_image",
                "",
            ]
        }

    def test_find_target_text_matches(self):
        expected = [
            (4, 5, 6),
            (17, 18, 19)
        ]
        actual = FindText.find_target_indices(self.ocr_result["text"], "Getting the bounding")
        self.assertEqual(expected, actual)

    def test_get_click_target_text(self):
        self.assertEqual("C", FindText.get_click_target_text(2))
        self.assertEqual("AA", FindText.get_click_target_text(26))
        self.assertEqual("AZ", FindText.get_click_target_text(51))
        self.assertEqual("AAT", FindText.get_click_target_text(71))
