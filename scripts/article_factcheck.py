"""Verify the two reviewed article versions against local World Cup records."""
import argparse
import csv
import hashlib
import importlib.util
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from operator import gt, lt
from statistics import mean

ARTICLES = {
    "article.md": "b7c0ef743e0d264707788ac95140cea8345e9896ffe1b44bbf7f479b111a0ebc",
    "WHY_NOT_KOREA_Final_Article.md": "01cf3bd45e86d09a9be4360a24acb2236cd9f9e917578cfb22bfe59f917022cf",
}
YEARS = tuple(range(2002, 2023, 4))
SCOPE = "2002~2022 FIFA 남자 월드컵 본선 6개 대회 · 384경기 · 팀·대회 기록 192건"
STATUSES = ("PASS", "FAIL", "HOLD", "REVIEW")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def article_digest(path):
    # Git may change line endings on checkout without changing the reviewed text.
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def sentences(article):
    for line, raw in enumerate(article.splitlines(), 1):
        raw = raw.strip()
        for sentence in [raw] if raw.startswith("#") else re.split(r"(?<=[.!?])\s+", raw):
            if sentence:
                yield line, sentence


def verdict(checks, causal=False):
    if causal:
        return "REVIEW"
    if any(c["matches"] is False for c in checks):
        return "FAIL"
    if not checks or any(c["matches"] is None for c in checks):
        return "HOLD"
    return "PASS"


class Evidence:
    def __init__(self, root):
        self.root = root
        self.refs = {}
        self.annual = defaultdict(Counter)
        self.match_rows = defaultdict(set)
        provenance = json.loads((root / "data/provenance.json").read_text(encoding="utf-8"))
        self.tables = {}
        for name in ("matches", "tournament_standings", "tournaments", "country_summary",
                     "korea_summary", "top10_comparison", "champion_summary",
                     "korea_positions", "legacy_comparison"):
            path = f"data/{name}.csv"
            sha = digest(root / path)
            expected = provenance.get(name + ".csv")
            provenance_sha = sha
            if expected and expected.get("hash_normalization") == "CRLF-to-LF":
                provenance_sha = hashlib.sha256((root / path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            if expected and provenance_sha != expected["sha256"]:
                raise ValueError(f"Provenance hash mismatch: {path}")
            with (root / path).open(encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                rows = []
                while True:
                    line = reader.line_num + 1 if reader.line_num else 2
                    row = next(reader, None)
                    if row is None:
                        break
                    rows.append((line, row))
            self.tables[name] = (path, sha, rows)
        self.tournaments = self.period_rows("tournaments")
        matches = self.period_rows("matches")
        self.standings = self.period_rows("tournament_standings")
        if (Counter(r["tournament_id"] for _, r in matches)
                != {f"WC-{y}": 64 for y in YEARS}
                or len({r["match_id"] for _, r in matches}) != 384):
            raise ValueError("Unexpected match coverage")
        for line, row in matches:
            year = int(row["tournament_id"][-4:])
            for side, opponent in (("home", "away"), ("away", "home")):
                key = year, row[f"{side}_team_code"]
                gf, ga = int(row[f"{side}_team_score"]), int(row[f"{opponent}_team_score"])
                self.annual[key].update(games=1, wins=int(gf > ga), draws=int(gf == ga),
                                        losses=int(gf < ga), gf=gf, ga=ga)
                self.match_rows[key].add(line)
        self.ranks = {(int(r["tournament_id"][-4:]), r["team_code"]): int(r["position"])
                      for _, r in self.standings}
        if (not set(self.ranks) <= set(self.annual) or len(self.standings) != 24
                or any(sorted(rank for (y, _), rank in self.ranks.items() if y == year)
                       != [1, 2, 3, 4] for year in YEARS)
                or any(Counter(c["games"] for (y, _), c in self.annual.items() if y == year)
                       != {3: 16, 4: 8, 5: 4, 7: 4} for year in YEARS)):
            raise ValueError("Unexpected standings coverage")
        self.countries = {code: self.total(self.keys(code)) for _, code in self.annual}
        self.top = sorted(self.countries, key=lambda code: (
            -self.countries[code]["wins"],
            self.countries[code]["ga"] - self.countries[code]["gf"],
            -self.countries[code]["gf"], code))[:10]
        self.champions = [key for key, rank in self.ranks.items() if rank == 1]
        self.match_columns = ("tournament_id", "match_id", "home_team_code", "away_team_code",
                              "home_team_score", "away_team_score", "penalty_shootout")
        self.rank_columns = ("tournament_id", "team_code", "position")
        self.notebook = "WHY_NOT_KOREA_WorldCup_Analysis.ipynb"
        notebook = json.loads((root / self.notebook).read_text(encoding="utf-8"))
        self.sheet = {}
        for index, cell in enumerate(notebook["cells"]):
            for output in cell.get("outputs", []):
                saved = "".join(output.get("text", []))
                if "Fact Sheet 생성 완료!" in saved and "[상관관계]" in saved:
                    for section in re.split(r"^\[([^\]\n]+)\]\s*$", saved, flags=re.M)[1:][::2]:
                        start = saved.index(f"[{section}]")
                        end = re.search(r"\n\[|\n분석 한계:", saved[start:])
                        excerpt = saved[start:start + end.start()] if end else saved[start:]
                        key = "FS-" + section
                        self.sheet[section] = key
                        self.refs[key] = dict(path=self.notebook, cell_index=index,
                                              sha256=digest(root / self.notebook),
                                              excerpt=excerpt.strip())
                    return
        raise ValueError("Saved Fact Sheet output missing")

    def period_rows(self, name):
        return [(line, r) for line, r in self.tables[name][2]
                if r["tournament_id"] in {f"WC-{year}" for year in YEARS}]

    def keys(self, code, year=None):
        return [key for key in self.annual if key[1] == code and year in (None, key[0])]

    def total(self, keys):
        total = Counter()
        for key in keys:
            total.update(self.annual[key])
        return dict(total, scored=total["gf"]/total["games"],
                    conceded=total["ga"]/total["games"],
                    win_rate=100*total["wins"]/total["games"])

    def ref(self, key, table, rows, columns):
        path, sha, _ = self.tables[table]
        self.refs[key] = dict(path=path, rows=sorted(set(rows)), columns=list(columns), sha256=sha)
        return key

    def match_ref(self, label, keys):
        return self.ref("M-" + label, "matches",
                        (line for key in keys for line in self.match_rows[key]), self.match_columns)

    def rank_ref(self, label, keys):
        keys = set(keys)
        return self.ref("R-" + label, "tournament_standings",
                        (line for line, r in self.standings
                         if (int(r["tournament_id"][-4:]), r["team_code"]) in keys),
                        self.rank_columns)

    def summary(self, table, code, year, column):
        found = [(n, r) for n, r in self.tables[table][2]
                 if r["code"] == code and (year is None or int(r["year"]) == year)]
        if len(found) != 1:
            return None, []
        n, row = found[0]
        key = self.ref(f"S-{table}-{code}-{year}-{column}", table, [n], [column])
        return float(row[column]), [key]


def check(metric, claimed, observed, method, refs=(), digits=None, consistent=True):
    comparable = observed if digits is None or observed is None else round(observed, digits)
    return dict(metric=metric, claimed=claimed, observed=observed, displayed=comparable,
                matches=None if observed is None or not consistent else claimed == comparable,
                calculation=method, evidence=list(refs))


def reviewed_claims(e, rag):
    korea, annual = e.keys("KOR"), e.keys("KOR", 2002)
    all_keys = list(e.annual)
    all_matches = e.match_ref("all", all_keys)
    scope_ref = e.ref("T-period", "tournaments", (n for n, _ in e.tournaments),
                      ["tournament_id", "tournament_name", "year"])
    scope = check("남자 월드컵 본선 대회 연도", list(YEARS),
                  sorted(int(r["year"]) for _, r in e.tournaments
                         if "FIFA Men's World Cup" in r["tournament_name"]),
                  "본선 대회 ID 및 연도 검색", [scope_ref])
    country_sheet = e.sheet["국가별 비교"]
    korea_sheet = e.sheet["대한민국 대회별 성적"]
    methods = dict(games="경기 행 수", wins="정규·연장 스코어 득점 > 실점인 경기 수",
                   draws="득점 = 실점인 경기 수", losses="득점 < 실점인 경기 수",
                   gf="팀 득점 합계", ga="팀 실점 합계", scored="총득점 ÷ 경기 수",
                   conceded="총실점 ÷ 경기 수", win_rate="승리 수 ÷ 경기 수 × 100")

    def metric(code, column, expected, digits=None, year=None):
        keys = e.keys(code, year)
        period = year or "2002–2022"
        source = e.match_ref(f"{code}-{period}", keys)
        raw = e.total(keys)[column]
        summary, refs = e.summary("korea_summary" if year else "country_summary",
                                  code, year, column)
        if code == "KOR" and column in {"games", "wins", "gf", "ga", "win_rate"}:
            term = rag.METRICS[column][0]
            facts, _ = rag.retrieve(f"대한민국 {year or '2002~2022'} {term}")
            refs.extend(f["id"] for f in facts if f["column"] == column)
            for fact in facts:
                e.refs[fact["id"]] = dict(path=fact["source"], rows=[fact["line"]],
                                          columns=[fact["column"]], sha256=fact["sha256"])
        sheet = [korea_sheet if year else country_sheet] if code in {
            "KOR", "DEU", "BRA", "ARG"} else []
        if code == "ARG" and column in {"wins", "win_rate"}:
            legacy_rows = [n for n, r in e.tables["legacy_comparison"][2] if r["team"] == "Argentina"]
            refs.append(e.ref("S-ARG-legacy", "legacy_comparison", legacy_rows,
                              ["Country", "Games", "Wins", "승률(%)", "wins", "win_rate",
                               "shootout_wins", "wins_with_shootout"]))
        return check(f"{period} {code} {column}", expected, raw, methods[column],
                     [source, *refs, *sheet], digits,
                     consistent=summary is not None and abs(summary-raw) < 1e-9)

    def kor(column, value, digits=None):
        return metric("KOR", column, value, digits)

    def k02(column, value, digits=None):
        return metric("KOR", column, value, digits, 2002)

    def compare(column, codes, op, expected):
        observed = op(codes, key=lambda code: e.countries[code][column])
        return check(f"{column} 비교 집단 극값", expected, observed,
                     f"{', '.join(codes)}의 {methods[column]} 비교", [all_matches, scope_ref])

    four = ["KOR", "ARG", "BRA", "DEU"]
    chosen = list(dict.fromkeys([*e.top, "KOR"]))
    extrema = [compare("scored", four, min, "KOR"), compare("conceded", four, max, "KOR")]
    total = [scope, kor("games", 24), kor("wins", 7)]
    goals = [kor("gf", 28), kor("ga", 35)]
    rates = [kor("scored", 1.17, 2), kor("conceded", 1.46, 2)]
    positions = e.tables["korea_positions"][2]
    ranks = {int(r["year"]): int(r["position"]) for _, r in positions}
    rank_ref = e.ref("R-KOR-annual", "korea_positions", (n for n, _ in positions), ["year", "position"])
    best = min(ranks, key=ranks.get)
    rank = [check("한국 분석 기간 최고 성적", [2002, 4], [best, ranks[best]],
                  "한국의 6개 대회 최종 순위 최솟값 및 상위 4위 CSV 대조",
                  [rank_ref, e.rank_ref("KOR", korea), korea_sheet],
                  consistent=len(positions) == len(YEARS) and set(ranks) == set(YEARS)
                  and all(ranks[y] == e.ranks[(y, "KOR")] for y, c in e.ranks if c == "KOR"))]
    wins = [metric(code, "wins", 23) for code in ("DEU", "BRA")]
    draws = [check("승부차기 경기의 경기 스코어", True,
                   all(r["home_team_score"] == r["away_team_score"]
                       for _, r in e.period_rows("matches") if r["penalty_shootout"] == "1"),
                   "정규·연장 동점은 무승부로 집계. 승부차기 득점 및 결과는 별도",
                   [all_matches])]
    champions = e.total(e.champions)
    champ_refs = [e.rank_ref("champions", e.champions), e.match_ref("champions", e.champions)]
    champ_count = check("우승팀 수", 6, len(e.champions), "대회별 최종 순위 1위", champ_refs)
    champ_ga = check("우승팀 경기당 실점", .62, champions["conceded"],
                     "6개 우승팀 실점 합 ÷ 경기 합", champ_refs, 2)
    champ_gf = check("우승팀 경기당 득점", 2.02, champions["scored"],
                     "6개 우승팀 득점 합 ÷ 경기 합", champ_refs, 2)

    def relation(label, left, right, op, refs):
        return check(label, True, op(left, right), "반올림 전 두 값 비교", refs)

    k02_total, kor_total = e.total(annual), e.total(korea)
    k_refs = [e.match_ref("KOR-2002", annual), e.match_ref("KOR-2002–2022", korea)]
    lower_gf = relation("2002 득점률 < 한국 전체", k02_total["scored"], kor_total["scored"], lt, k_refs)
    lower_ga = relation("2002 실점률 < 한국 전체", k02_total["conceded"], kor_total["conceded"], lt, k_refs)
    higher_ga = relation("2002 실점률 > 우승팀 평균", k02_total["conceded"],
                         champions["conceded"], gt, [*k_refs, *champ_refs])
    stage_refs = [all_matches, e.sheet["최종 성적별 비교"]]
    counts, stage_rates = [], []
    for name, games, count, gf, ga in [
        ("조별리그 탈락", 3, 96, .826, 1.694),
        ("16강 탈락", 4, 48, 1.240, 1.255),
        ("8강 탈락", 5, 24, 1.642, .808),
        ("4강 진출", 7, 24, 1.738, .827),
    ]:
        keys = [key for key, c in e.annual.items() if c["games"] == games]
        counts.append(check(name, count, len(keys), f"{games}경기를 치른 팀·대회 기록 수", stage_refs))
        for column, expected in (("scored", gf), ("conceded", ga)):
            stage_rates.append(check(f"{name} {column}", expected,
                                     mean(e.total([key])[column] for key in keys),
                                     f"팀·대회별 {methods[column]}의 산술평균", stage_refs, 3))
    stage_labels = check("16강·8강 비교 집단", "진출 팀 전체", "각 단계 탈락 팀",
                         "원고 집단 명칭과 중복 없는 최종 성적 분류 대조", stage_refs)
    correlation_refs = [all_matches, e.rank_ref("podium", e.ranks), e.sheet["상관관계"]]
    correlations = [check(f"192개 팀·대회 순위 × {column}", expected, None,
                          "저장 Fact Sheet 수치는 확인. 순위 CSV는 대회별 1~4위만 있어 전체 피어슨 계수 재계산 불가",
                          correlation_refs)
                    for column, expected in (("scored", -.678), ("conceded", .637))]
    directions = [check(c["metric"] + " 방향", c["claimed"] > 0, None,
                        c["calculation"], c["evidence"]) for c in correlations]
    top_ref = e.ref("S-top10", "top10_comparison",
                    (n for n, _ in e.tables["top10_comparison"][2]),
                    ["code", "selection_order", "wins", "scored", "conceded", "win_rate"])
    top_group = check("누적 승수 상위 10개국 및 한국", chosen,
                      [r["code"] for _, r in e.tables["top10_comparison"][2]],
                      "승수→득실차→득점 내림차순, 국가 코드 오름차순으로 10개국 선별 후 한국 추가",
                      [all_matches, top_ref])
    source = check("경기 CSV 계보", True,
                   "jfjelstul/worldcup/" in json.loads(
                       (e.root / "data/provenance.json").read_text(encoding="utf-8")
                   )["matches.csv"]["url"],
                   "data/provenance.json의 출처 및 SHA-256 확인", [all_matches])
    new = {
        0: total + [goals[1]], 1: total, 2: goals, 3: [kor("win_rate", 29.2, 1)], 4: draws,
        5: [scope, top_group, *rates, compare("scored", chosen, min, "KOR"),
            compare("conceded", chosen, max, "KOR")],
        6: wins, 7: [top_group, metric("NLD", "wins", 16), metric("NLD", "games", 23),
                     metric("NLD", "win_rate", 69.6, 1),
                     compare("win_rate", chosen, max, "NLD")],
        8: rank, 9: [k02("conceded", .86, 2)],
        10: [champ_count, champ_ga, rates[1], lower_ga, higher_ga],
        11: [k02("scored", 1.14, 2), champ_gf],
        14: [scope], 15: [source],
    }
    old = {
        1: total + extrema,
        3: [compare("win_rate", four, min, "KOR")],
        4: total, 5: goals + rates,
        6: [metric(code, "scored", v, 2) for code, v in zip(four[1:], [1.68, 1.88, 2.06])],
        7: [metric(code, "conceded", v, 2) for code, v in zip(four[1:], [1.03, .88, .79])],
        8: [metric(code, "win_rate", v, 1) for code, v in zip(four, [29.2, 64.5, 67.6, 67.6])],
        9: wins + [metric(code, "games", v) for code, v in zip(four[1:], [31, 34, 34])]
        + [metric("ARG", "wins", 20)],
        10: [check("국가별 경기 수 차이", True, len({e.countries[c]["games"] for c in four}) > 1,
                   "네 나라 경기 수의 고유값 개수 비교", [all_matches])],
        11: extrema, 13: draws, 14: rank, 15: rank,
        16: [k02(column, value) for column, value in zip(
            ["games", "wins", "draws", "losses", "gf", "ga"], [7, 3, 2, 2, 8, 6])],
        17: [k02("scored", 1.14, 2), k02("conceded", .86, 2)],
        18: [rates[0], lower_gf], 19: [k02("conceded", .86, 2), rates[1], lower_ga],
        20: [check("한국 4강 기록 수", 1, sum(pos <= 4 for pos in ranks.values()),
                   "한국 최종 순위 1~4위 기록 수", [rank_ref])],
        22: counts + [stage_labels], 24: stage_rates + [stage_labels], 25: correlations, 26: directions,
        28: [check("원래 Kaggle 데이터셋 식별", "원본 URL 및 버전", None,
                   "저장된 Fact Sheet에 출처 명칭만 있고 원본 URL과 버전을 확인할 근거 없음",
                   list(e.sheet.values()))],
        29: [scope],
        30: [check("원고가 사용한 자료의 단위", "팀·대회 집계", "팀·대회 집계",
                   "노트북 저장 Fact Sheet의 대한민국 대회별 성적과 비교 표 구조 확인",
                   [korea_sheet, country_sheet])],
        31: [check("FIFA 공식 자료 독립 대조", "완료 여부", None,
                   "노트북의 당시 한계는 확인. 현재 공식 자료 대조는 이 실행 범위 밖",
                   [korea_sheet])],
    }
    edits = {
        "article.md": {
            8: "2002~2022년 6개 대회 중 대한민국의 최고 성적은 2002년 4위였다.",
        },
        "WHY_NOT_KOREA_Final_Article.md": {
            0: "2002~2022 월드컵에서 한국의 득점·실점은 비교 국가와 어떻게 달랐나",
            8: "승률은 브라질과 독일이 각각 67.6%, 아르헨티나가 58.1%, 한국이 29.2%였다.",
            9: "브라질과 독일은 각각 34경기에서 23승, 아르헨티나는 31경기에서 18승을 기록했다.",
            22: "팀·대회 기록은 조별리그 탈락 96건, 16강 탈락 48건, 8강 탈락 24건, 4강 진출 24건이다.",
            24: "조별리그 탈락 팀은 경기당 0.826득점·1.694실점, 8강 탈락 팀은 1.642득점·0.808실점, 16강 탈락 팀은 1.240득점·1.255실점, 4강 진출 팀은 1.738득점·0.827실점이었다.",
            25: "192개 팀·대회의 최종 순위를 확보해 상관계수를 재계산할 때까지 수치 인용을 보류한다.",
            26: "전체 최종 순위를 확보해 상관관계의 방향을 확인한 뒤 서술한다.",
            28: "Kaggle 원본 URL과 버전을 확인한 뒤 명시한다. 개별 경기 재검증 출처는 Fjelstul World Cup Database로 표기한다.",
            31: "이번 팩트체크는 Fjelstul 경기·순위 CSV로 재계산했다. FIFA 공식 자료와의 대조 여부는 확인이 필요하다.",
        },
    }
    return dict(zip(ARTICLES, (new, old))), edits


def run(root):
    spec = importlib.util.spec_from_file_location("rag_qa", root / "scripts/rag_qa.py")
    rag = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rag)
    rag.load_instructions()
    evidence = Evidence(root)
    plans, edits = reviewed_claims(evidence, rag)
    results, excluded = [], []
    article_hashes = {name: article_digest(root / name) for name in ARTICLES}
    for article, reviewed_hash in ARTICLES.items():
        path = root / article
        reviewed = article_hashes[article] == reviewed_hash
        for i, (line, sentence) in enumerate(sentences(path.read_text(encoding="utf-8-sig"))):
            checks = plans[article].get(i, []) if reviewed else []
            # Review affirmative causal language and the older article's causal headline.
            causal = (reviewed and article != "article.md" and i == 0) or bool(re.search(
                r"(때문에|덕분에|원인이다|초래했다|입증한다)", sentence))
            if reviewed and not checks and not causal:
                excluded.append(dict(article=article, line=line, sentence=sentence))
                continue
            status = verdict(checks, causal)
            suggestion = edits[article].get(i, "") if reviewed else ""
            if status in {"FAIL", "HOLD", "REVIEW"} and not suggestion:
                suggestion = "재계산 값을 확인하고 근거 및 적용 범위를 명시한다." if checks else "문장과 검증 규칙을 다시 대조한다."
            results.append(dict(article=article, line=line, sentence=sentence, status=status,
                                checks=checks, suggestion=suggestion,
                                reason=("인과 프레이밍 검토" if causal else
                                        "기사 버전 변경으로 수동 매핑 재검토 필요" if not reviewed else
                                        "CSV 재계산과 기사 값 대조")))
    used = {ref for r in results for c in r["checks"] for ref in c["evidence"]}
    return dict(scope=SCOPE, sentence_count=len(results),
                counts={s: sum(r["status"] == s for r in results) for s in STATUSES},
                article_sha256=article_hashes,
                instructions_sha256=digest(root / "config/RAG_INSTRUCTIONS.md"),
                results=results, excluded=excluded,
                evidence={key: evidence.refs[key] for key in sorted(used)})


def row_ranges(rows):
    ranges = []
    for row in rows:
        if ranges and row == ranges[-1][-1] + 1:
            ranges[-1].append(row)
        else:
            ranges.append([row])
    return ", ".join(str(r[0]) if len(r) == 1 else f"{r[0]}–{r[-1]}" for r in ranges)


def write_reports(report, output):
    folder = output / "reports"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "article_factcheck.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = " · ".join(f"{s} {n}" for s, n in report["counts"].items())
    intro = [
        f"검사 범위 — {report['scope']}",
        f"검사 문장 {report['sentence_count']}건 · {counts} · 범위 밖 {len(report['excluded'])}건",
        "제목·소제목의 주장도 문장 단위 집계에 포함했다. 같은 주장이 두 원고에 나오면 각각 집계했다.",
        "원고별로 검토한 문장 매핑을 적용했다. 기사 해시가 바뀌면 수동 재검토 대상으로 넘긴다.",
        "검증 우선순위는 개별 경기·최종 순위 CSV 재계산이다. 노트북의 저장 Fact Sheet는 원고 수치의 계보와 불일치를 찾는 데 사용했다.",
        "승부차기 승리는 승수에서 제외했다. 표시 자릿수로 반올림해 대조했다. FIFA 공식 자료는 검사 범위 밖이다.",
        "PASS는 아래 열거한 검사 항목에 적용된다. 같은 문장에 들어 있는 편집적 해석은 수치 판정에서 제외했다.",
    ]
    lines = ["# 기사 팩트체크", "", *intro, "", "## 문장별 결과", ""]
    revisions = ["# 문장별 수정 권고", "", *intro, ""]
    for result in report["results"]:
        heading = f"### {result['status']} · {result['article']} L{result['line']}"
        quote = "> " + result["sentence"]
        lines.extend([heading, "", quote, "", result["reason"], ""])
        for c in result["checks"]:
            refs = ", ".join(f"[{ref}](#evidence-{anchor(ref)})" for ref in c["evidence"])
            value = "확인 불가" if c["matches"] is None else c["displayed"]
            lines.append(f"- {c['metric']} · 기사 {c['claimed']} / 검증 {value} · {c['calculation']} · {refs}")
        lines.append("")
        if result["suggestion"]:
            revisions.extend([heading, "", quote, "", result["suggestion"], ""])
            for c in result["checks"]:
                if c["matches"] is False:
                    revisions.append(f"- {c['metric']} · {c['claimed']} → {c['displayed']} · {', '.join(c['evidence'])}")
            revisions.append("")
    lines.extend(["## 검사 범위 밖 문장", ""])
    lines.extend(f"- {x['article']} L{x['line']} · {x['sentence']}" for x in report["excluded"])
    lines.extend(["", "## 근거 위치", ""])
    for key, item in report["evidence"].items():
        location = (f"행 {row_ranges(item['rows'])} · 열 {', '.join(item['columns'])}"
                    if "rows" in item else f"저장 출력 셀 인덱스 {item['cell_index']} (0부터)")
        lines.extend([f'<a id="evidence-{anchor(key)}"></a>',
                      f"- **{key}** · `{item['path']}` · {location} · SHA-256 `{item['sha256']}`"])
    (folder / "article_factcheck.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (folder / "article_revision_suggestions.md").write_text("\n".join(revisions) + "\n", encoding="utf-8")
    print(f"{report['scope']}\n검사 문장 {report['sentence_count']}건 · {counts}")


def anchor(key):
    return re.sub(r"\s+", "-", key)


def render_png(report, output, font_path):
    from PIL import Image, ImageDraw, ImageFont

    lines = ["WHY NOT KOREA?  /  ARTICLE FACT-CHECK",
             "실제 CSV 재계산 결과 · article_factcheck.json", report["scope"],
             f"검사 문장 {report['sentence_count']}건   |   " +
             "   ".join(f"{s} {n}" for s, n in report["counts"].items()), ""]
    for status in STATUSES:
        result = next((r for r in report["results"] if r["status"] == status), None)
        if result is None:
            continue
        lines.append(f"{status}   {result['article']} · L{result['line']}")
        item = next((c for c in result["checks"] if c["matches"] is False),
                    next(iter(result["checks"]), None))
        if item:
            value = "확인 불가" if item["matches"] is None else item["displayed"]
            lines.append(f"   {item['metric']}   기사 {item['claimed']}  /  검증 {value}")
            if item["evidence"]:
                ref = item["evidence"][0]
                lines.append(f"   {ref}  |  {report['evidence'][ref]['path']}")
        else:
            lines.append(f"   {result['reason']}")
        lines.append("")
    font = ImageFont.truetype(str(font_path), 24)
    title = ImageFont.truetype(str(font_path), 32)
    image = Image.new("RGB", (1420, 42 * len(lines) + 68), "#101c2e")
    draw = ImageDraw.Draw(image)
    for i, line in enumerate(lines):
        draw.text((42, 34 + 42*i), line, font=title if i == 0 else font,
                  fill="#8ee4d2" if i < 4 or line.split(" ")[0] in STATUSES else "#e7eef8")
    path = output / "docs/rag_evidence/article_factcheck.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--png-font", type=Path, help="Render the run results with this Korean font")
    args = parser.parse_args()
    output = args.output or args.root
    report = run(args.root.resolve())
    write_reports(report, output)
    if args.png_font:
        render_png(report, output, args.png_font)
