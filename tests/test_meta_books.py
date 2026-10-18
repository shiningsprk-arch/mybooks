#!/usr/bin/env python3

import asyncio
import unittest
from unittest import mock

from webserver.handlers import meta
from webserver.handlers.meta import MetaBooks


class FakeCache:
    FIELDS = {
        "rating": {1: 4, 2: 8, 3: None, 4: 8},
        "series_index": {1: 2.0, 2: 1.0, 3: None, 4: 1.0},
        "sort": {1: "b", 2: "z", 3: "c", 4: "a"},
    }

    def all_field_for(self, field, ids, default):
        return {i: self.FIELDS[field].get(i, default) for i in ids}


def make_handler():
    handler = MetaBooks.__new__(MetaBooks)
    handler.calibre_db_cache = FakeCache()
    return handler


class TestMetaBooks(unittest.TestCase):

    def test_rating_sort_matches_rating_desc_then_id_desc(self):
        self.assertEqual(make_handler()._sorted_ids({1, 2, 3, 4}, "tag"), [4, 2, 1, 3])

    def test_series_sort_by_index_then_sort_key(self):
        self.assertEqual(make_handler()._sorted_ids({1, 2, 3, 4}, "series"), [3, 4, 2, 1])

    def test_new_sort(self):
        self.assertEqual(make_handler()._sorted_ids({1, 2, 3, 4}, "tag", "new"), [4, 3, 2, 1])

    def test_title_sort(self):
        self.assertEqual(make_handler()._sorted_ids({1, 2, 3, 4}, "tag", "title"), [4, 1, 3, 2])

    def test_random_sort_keeps_all_ids(self):
        result = make_handler()._sorted_ids({1, 2, 3, 4}, "tag", "random")
        self.assertEqual(sorted(result), [1, 2, 3, 4])

    def test_invalid_rating_returns_empty_without_raising(self):
        """公开路由 /api/rating/<name>：非 1-5 整数不能让 int() 抛给 @js。"""
        handler = make_handler()
        for bad in ("abc", "0", "6", "", "4.5"):
            self.assertEqual(handler._book_ids("rating", bad), set(), bad)

    def test_rating_reads_ratings_table_and_unions_categories(self):
        """rating 走 ratings 表的 0-10 原始分值（4 星 = 7/8），再按 item id 取书。"""
        handler = make_handler()
        handler.calibre_db_cache.backend = mock.Mock()
        handler.calibre_db_cache.backend.conn.get = mock.Mock(return_value=[(3,), (2,)])
        handler.calibre_db = mock.Mock()
        handler.calibre_db.get_books_for_category = (
            lambda category, item_id: {1, 2} if item_id == 2 else {3}
        )
        self.assertEqual(handler._book_ids("rating", "4"), {1, 2, 3})
        sql, params = handler.calibre_db_cache.backend.conn.get.call_args.args
        self.assertIn("FROM ratings", sql)
        self.assertEqual(params, (7, 8))

    def test_get_pages_ids_instead_of_loading_all_books(self):
        handler = make_handler()
        handler.get_argument = lambda name, default=None: {
            "sort": "new",
            "cover": "1",
        }.get(name, default)
        handler.run_calibre_async = mock.AsyncMock(return_value={1, 2, 3, 4})
        handler.run_calibre_read_async = mock.AsyncMock(return_value=[4, 2, 1, 3])
        handler.get_book_list = mock.AsyncMock(return_value={"err": "ok", "books": [{"id": 4}]})
        handler.request = mock.Mock()
        handler.request.headers = {}
        handler.written = None
        handler.set_header = lambda *args, **kwargs: None
        handler.write = lambda rsp: setattr(handler, "written", rsp)
        handler.finish = lambda: None
        with mock.patch.object(meta, "_", side_effect=lambda s: s):
            asyncio.run(MetaBooks.get(handler, "language", "中文"))
        self.assertEqual(handler.written, {"err": "ok", "books": [{"id": 4}]})
        handler.run_calibre_read_async.assert_awaited_once()
        sort_args = handler.run_calibre_read_async.await_args.args
        self.assertEqual(sort_args[2], "language")
        self.assertEqual(sort_args[3], "new")
        handler.get_book_list.assert_awaited_once()
        self.assertEqual(handler.get_book_list.await_args.kwargs["ids"], [4, 2, 1, 3])
        self.assertFalse(handler.get_book_list.await_args.kwargs["include_comments"])
        self.assertEqual(handler.get_book_list.await_args.args[0], [])


if __name__ == "__main__":
    unittest.main()
