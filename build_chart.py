"""수집한 CSV를 템플릿에 주입해 pbr_chart.html 을 만든다.

이동평균·엔벨로프·분위는 pandas 로 계산해 교차검증용 요약을 출력하고,
페이지에는 원본 시계열만 넣는다(그리기 직전에 JS 가 같은 식으로 재계산).
"""

import json
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
MA_WINDOW = 20
ENV = 0.20
SOURCES = {"kospi": "코스피", "kosdaq": "코스닥"}


def load(name: str) -> pd.DataFrame:
    df = pd.read_csv(
        BASE / f"{name}_raw.csv",
        header=None,
        names=["date", "close", "pbr", "per", "div"],
        dtype={"date": str},
    )
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    # KRX 는 미산출 구간을 0 으로 채워 내려준다. 결측으로 돌린다.
    for col in ("pbr", "per", "div"):
        df.loc[df[col] == 0, col] = pd.NA
    return df.sort_values("date").reset_index(drop=True)


def main() -> None:
    frames = {k: load(k) for k in SOURCES}

    dates = frames["kospi"]["date"]
    for name, df in frames.items():
        if not df["date"].equals(dates):
            raise SystemExit(f"{name} 의 날짜축이 코스피와 다릅니다. 개별 축이 필요합니다.")

    payload = {
        "maWindow": MA_WINDOW,
        "env": ENV,
        "dates": [d.strftime("%Y-%m-%d") for d in dates],
        "series": {},
    }

    for name, label in SOURCES.items():
        df = frames[name]
        ma = df["pbr"].rolling(MA_WINDOW).mean()
        pct = df["pbr"].rank(pct=True) * 100
        payload["series"][name] = {
            "label": label,
            "pbr": [None if pd.isna(v) else round(float(v), 4) for v in df["pbr"]],
            "close": [None if pd.isna(v) else float(v) for v in df["close"]],
            "per": [None if pd.isna(v) else float(v) for v in df["per"]],
            "div": [None if pd.isna(v) else float(v) for v in df["div"]],
        }
        last = len(df) - 1
        print(
            f"[{label}] {len(df)}행  {df['date'].iloc[0]:%Y-%m-%d} ~ {df['date'].iloc[last]:%Y-%m-%d}\n"
            f"  PBR  최저 {df['pbr'].min():.2f} / 최고 {df['pbr'].max():.2f} / 최근 {df['pbr'].iloc[last]:.2f}\n"
            f"  20일 이평 최근 {ma.iloc[last]:.4f}  상단 {ma.iloc[last]*(1+ENV):.4f}  하단 {ma.iloc[last]*(1-ENV):.4f}\n"
            f"  이평대비 {(df['pbr'].iloc[last]/ma.iloc[last]-1)*100:+.2f}%  역사분위 {pct.iloc[last]:.1f}%\n"
            f"  상단 이탈 {int((df['pbr'] > ma*(1+ENV)).sum())}일 / 하단 이탈 {int((df['pbr'] < ma*(1-ENV)).sum())}일"
        )

    tpl = (BASE / "pbr_chart_template.html").read_text(encoding="utf-8")
    out = tpl.replace("__DATA__", json.dumps(payload, separators=(",", ":")))
    (BASE / "pbr_chart.html").write_text(out, encoding="utf-8")
    print(f"\n-> pbr_chart.html ({len(out):,} bytes)")


if __name__ == "__main__":
    main()
