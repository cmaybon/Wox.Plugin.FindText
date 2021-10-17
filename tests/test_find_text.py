import unittest
from unittest import TestCase

import find_text


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
                "the",
                "screen_image",
                "",
            ]
        }
        pass

    def test_find_target_text_matches(self):
        expected = [
            (4, 5, 6),
            (17, 18)
        ]
        actual = find_text.find_target_indices(self.ocr_result["text"], "Getting the bounding")
        self.assertEqual(expected, actual)
