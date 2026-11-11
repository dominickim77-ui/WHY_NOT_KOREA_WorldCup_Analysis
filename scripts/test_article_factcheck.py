import csv
import os
from pathlib import Path
import unittest

from article_factcheck import ARTICLES, digest, run, verdict


class ArticleFactcheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(os.environ.get("WORLD_CUP_ROOT", Path(__file__).resolve().parents[1]))
        cls.report = run(cls.root)

    def test_article_versions_and_counts(self):
        self.assertEqual(self.report["article_sha256"], ARTICLES)
        self.assertEqual(self.report["sentence_count"], sum(self.report["counts"].values()))
        self.assertEqual(self.report["counts"], dict(PASS=32, FAIL=4, HOLD=4, REVIEW=1))

    def test_argentina_conflict_and_missing_rank_scope(self):
        checks = {c["metric"]: c for r in self.report["results"] for c in r["checks"]}
        wins = checks["2002–2022 ARG wins"]
        self.assertEqual((wins["claimed"], wins["observed"], wins["matches"]), (20, 18, False))
        self.assertEqual(checks["2002–2022 ARG win_rate"]["displayed"], 58.1)
        self.assertIsNone(checks["192개 팀·대회 순위 × scored"]["matches"])

    def test_csv_evidence_coordinates_and_hashes(self):
        for item in self.report["evidence"].values():
            path = self.root / item["path"]
            self.assertEqual(digest(path), item["sha256"])
            if "rows" not in item:
                self.assertTrue(item["excerpt"])
                continue
            with path.open(encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                self.assertTrue(set(item["columns"]) <= set(reader.fieldnames))
                rows = set()
                while True:
                    line = reader.line_num + 1
                    if next(reader, None) is None:
                        break
                    rows.add(line)
                self.assertTrue(item["rows"])
                self.assertTrue(set(item["rows"]) <= rows)

    def test_fail_closed_and_causal_review(self):
        self.assertEqual(verdict([]), "HOLD")
        self.assertEqual(verdict([{"matches": None}]), "HOLD")
        self.assertEqual(verdict([{"matches": True}], causal=True), "REVIEW")
        for row in self.report["results"]:
            if row["status"] == "PASS":
                self.assertTrue(row["checks"])
                self.assertTrue(all(c["matches"] is True and c["evidence"] for c in row["checks"]))
