"""Rank candidate genres by expected monthly revenue.

expected = monthly_volume * rank_chance * ctr * cvr * payout_jpy
rank_chance = (individual blogs in SERP sample / sample size), floored at 0.02 for a
brand-new site (a head term with no individual blog in the top results is treated as
almost unwinnable). volume is filled by the owner from Google Keyword Planner / Ahrefs.
Rows with no volume are reported as 'needs volume'."""
import csv
import sys
from collections import defaultdict
from pathlib import Path

FLOOR = 0.02


def rank_chance(blogs, sample):
    return max(FLOOR, blogs / sample) if sample else FLOOR


def expected(row):
    vol = row["monthly_volume"].strip()
    if not vol:
        return None
    return (float(vol) * rank_chance(int(row["serp_individual_blogs"]), int(row["serp_sample"]))
            * float(row["ctr"]) * float(row["cvr"]) * float(row["payout_jpy"]))


def summarize(path):
    totals, missing = defaultdict(float), defaultdict(int)
    for row in csv.DictReader(open(path, encoding="utf-8")):
        e = expected(row)
        if e is None:
            missing[row["genre"]] += 1
        else:
            totals[row["genre"]] += e
    return dict(totals), dict(missing)


if __name__ == "__main__":
    t, m = summarize(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).with_name("keywords.csv"))
    for g in sorted(set(t) | set(m)):
        print(f"{g}: expected {t.get(g, 0):,.0f} JPY/month, rows needing volume: {m.get(g, 0)}")
