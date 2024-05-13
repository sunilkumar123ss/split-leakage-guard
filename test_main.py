import unittest
from main import audit


def record(name, text, split, **kwargs):
    return dict(id=name, text=text, split=split, **kwargs)


class LeakageTests(unittest.TestCase):
    def test_unicode_case_and_whitespace_duplicate(self):
        result = audit([record("a", "ＦＯＯ  bar", "train"), record("b", "foo bar", "test")])
        self.assertEqual(len(result["findings"]["exact_cross_split"]), 1)
        self.assertFalse(result["passed"])

