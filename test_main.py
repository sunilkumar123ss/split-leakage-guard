import unittest
from main import audit


def record(name, text, split, **kwargs):
    return dict(id=name, text=text, split=split, **kwargs)


class LeakageTests(unittest.TestCase):
    def test_unicode_case_and_whitespace_duplicate(self):
        result = audit([record("a", "ＦＯＯ  bar", "train"), record("b", "foo bar", "test")])
        self.assertEqual(len(result["findings"]["exact_cross_split"]), 1)
        self.assertFalse(result["passed"])

    def test_group_and_near_duplicate(self):
        rows = [record("a", "one two three four", "train", group="speaker-1"),
                record("b", "one two three five", "test", group="speaker-1")]
        result = audit(rows, near_threshold=0.6)
        self.assertEqual(len(result["findings"]["shared_groups"]), 1)
        self.assertEqual(result["findings"]["near_duplicate_candidates"][0]["token_jaccard"], 0.6)

    def test_same_split_is_not_cross_split_leak(self):
        rows = [record("a", "same text", "train"), record("b", "same text", "train")]
        self.assertTrue(audit(rows)["passed"])
        self.assertTrue(audit([])["passed"])

