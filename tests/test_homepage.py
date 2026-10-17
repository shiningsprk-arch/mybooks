#!/usr/bin/env python3

import unittest

from webserver.base.homepage import (
    BUILTIN_SECTIONS,
    MAX_CUSTOM_CARDS,
    default_homepage,
    homepage_from_legacy,
    normalize_homepage,
)


class TestHomepageConfig(unittest.TestCase):

    def test_default(self):
        config = normalize_homepage({})
        self.assertEqual(config["version"], 1)
        self.assertEqual(config["order"], list(BUILTIN_SECTIONS))
        self.assertEqual(config["hidden"], [])
        self.assertEqual(config["custom"], [])

    def test_unknown_sections_are_dropped_and_missing_appended(self):
        config = normalize_homepage(
            {
                "order": ["unknown", "index.myReading", "custom:c1", "index.myReading"],
                "hidden": ["unknown", "index.myReading"],
                "custom": [{"id": "c1", "type": "author", "value": "刘慈欣"}],
            }
        )
        self.assertEqual(
            config["order"],
            [
                "index.myReading",
                "custom:c1",
                "libraryStats",
                "readingStats",
                "index.socialRecommendation",
                "index.booklistRecommendation",
                "index.randomRecommendation",
                "index.newRecommendation",
            ],
        )
        self.assertEqual(config["order"].count("index.myReading"), 1)
        self.assertNotIn("unknown", config["order"])
        self.assertEqual(config["hidden"], ["index.myReading"])
        self.assertEqual(set(config["order"]), set(BUILTIN_SECTIONS) | {"custom:c1"})

    def test_custom_card_normalization(self):
        config = normalize_homepage(
            {
                "custom": [
                    {
                        "id": "bad id",
                        "type": "series",
                        "value": "  三体  ",
                        "sort": "bad",
                        "limit": 999,
                    },
                    {"id": "dup", "type": "tag", "value": "科幻"},
                    {"id": "dup", "type": "tag", "value": "奇幻"},
                ]
            }
        )
        cards = config["custom"]
        self.assertEqual(cards[0]["id"], "c1")
        self.assertEqual(cards[0]["value"], "三体")
        self.assertNotIn("title", cards[0])
        self.assertEqual(cards[0]["sort"], "series")
        self.assertEqual(cards[0]["limit"], 12)
        self.assertEqual(cards[1]["id"], "dup")
        self.assertNotEqual(cards[2]["id"], "dup")

    def test_unknown_type_skipped_empty_value_kept(self):
        config = normalize_homepage(
            {
                "custom": [
                    {"type": "unknown", "value": "x"},
                    {"type": "author", "value": "   "},
                    {"type": "author", "value": "OK", "limit": 24},
                    {"type": "tag", "value": {"bad": 1}},
                ]
            }
        )
        self.assertEqual(len(config["custom"]), 3)
        self.assertEqual(config["custom"][0]["value"], "")
        self.assertEqual(config["custom"][1]["value"], "OK")
        self.assertEqual(config["custom"][1]["limit"], 24)
        self.assertEqual(config["custom"][2]["value"], "")

    def test_custom_card_limit(self):
        cards = [
            {"id": "c%d" % i, "type": "author", "value": "a%d" % i}
            for i in range(MAX_CUSTOM_CARDS + 10)
        ]
        config = normalize_homepage({"custom": cards})
        self.assertEqual(len(config["custom"]), MAX_CUSTOM_CARDS)

    def test_bad_root_returns_default(self):
        self.assertEqual(normalize_homepage(None), default_homepage())
        self.assertEqual(normalize_homepage([]), default_homepage())

    def test_legacy_flags_become_hidden_sections(self):
        config = homepage_from_legacy(
            {
                "ENABLE_HOMEPAGE_READING_STATS": False,
                "ENABLE_HOMEPAGE_READING_BOOKS": False,
                "ENABLE_HOMEPAGE_BOOKLISTS": False,
                "ENABLE_BOOK_RECOMMEND_TO_OTHERS": False,
                "MAIN_PAGE_RANDOM_COUNT": 0,
            }
        )
        self.assertEqual(
            set(config["hidden"]),
            {
                "readingStats",
                "index.myReading",
                "index.booklistRecommendation",
                "index.socialRecommendation",
                "index.randomRecommendation",
            },
        )

    def test_legacy_defaults_hide_booklists(self):
        config = homepage_from_legacy({})
        self.assertEqual(config["hidden"], ["index.booklistRecommendation"])


if __name__ == "__main__":
    unittest.main()
