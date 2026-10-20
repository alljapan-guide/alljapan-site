import csv
from validation.estimate import expected, rank_chance, summarize


def row(**kw):
    base = dict(genre="g", keyword="k", monthly_volume="1000", serp_individual_blogs="5", serp_sample="10",
                payout_jpy="1000", ctr="0.1", cvr="0.01")
    base.update(kw)
    return base


def test_hand_calc():
    # 1000 * 0.5 * 0.1 * 0.01 * 1000 = 500
    assert expected(row()) == 500.0


def test_floor_and_missing_volume():
    assert rank_chance(0, 10) == 0.02
    assert expected(row(monthly_volume="")) is None


def test_summarize(tmp_path):
    p = tmp_path / "k.csv"
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row().keys()))
        w.writeheader(); w.writerows([row(), row(monthly_volume="")])
    assert summarize(p) == ({"g": 500.0}, {"g": 1})
