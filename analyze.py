from pathlib import Path
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
CHARTS = ROOT / "charts"
YEARS = list(range(2002, 2023, 4))
IDS = [f"WC-{year}" for year in YEARS]
RED, BLUE, GRAY = "#bd293e", "#275880", "#64788a"
KO = dict(BRA="브라질", DEU="독일", ARG="아르헨티나", FRA="프랑스", ESP="스페인",
          NLD="네덜란드", ENG="잉글랜드", PRT="포르투갈", ITA="이탈리아",
          HRV="크로아티아", BEL="벨기에", KOR="대한민국", URY="우루과이", MEX="멕시코")
GROUPS = ["4강 진출", "8강 탈락", "16강 탈락", "조별리그 탈락"]
FILES = [
    "01_korea_worldcup_rank", "02_country_goals_comparison",
    "03_korea_2002_vs_champions", "04_stage_goal_difference",
    "05_country_win_rate", "06_country_scatter",
    "07_korea_correlation_heatmap", "08_korea_goals_boxplot",
]

def load(name):
    frame = pd.read_csv(DATA / f"{name}.csv")
    return frame.loc[frame.tournament_id.isin(IDS)].copy()

def rates(frame):
    return frame.assign(scored=frame.gf / frame.games,
                        conceded=frame.ga / frame.games,
                        margin=(frame.gf - frame.ga) / frame.games,
                        win_rate=100 * frame.wins / frame.games)

def analyze():
    matches = load("matches")
    podium = load("tournament_standings")
    tournaments = load("tournaments")
    assert matches.groupby("tournament_id").size().to_dict() == dict.fromkeys(IDS, 64)
    assert matches.match_id.is_unique
    assert matches.groupby(["tournament_id", "stage_name"]).size().unstack().eq({
        "group stage": 48, "round of 16": 8, "quarter-finals": 4,
        "semi-finals": 2, "third-place match": 1, "final": 1,
    }).all().all()
    scores = matches[["home_team_score", "away_team_score"]]
    assert scores.notna().all().all() and scores.ge(0).all().all()
    assert matches.penalty_shootout.isin([0, 1]).all()
    shootouts = matches.loc[matches.penalty_shootout.eq(1)]
    assert shootouts.home_team_score.eq(shootouts.away_team_score).all()
    assert shootouts.home_team_score_penalties.ne(shootouts.away_team_score_penalties).all()

    independent = pd.read_csv(DATA / "independent_scores.csv")
    edition = independent.date.str.startswith("2006")
    teams = ["home_team", "away_team"]
    independent.loc[edition, teams] = independent.loc[edition, teams].replace(
        {"Serbia": "Serbia and Montenegro"}
    )
    def score_keys(rows):
        return sorted((day, *sorted([(home, gf), (away, ga)]))
                      for day, home, away, gf, ga in rows.itertuples(index=False, name=None))

    assert score_keys(independent) == score_keys(matches[
        ["match_date", "home_team_name", "away_team_name", "home_team_score", "away_team_score"]
    ])

    parts = []
    for side, other in [("home", "away"), ("away", "home")]:
        parts.append(pd.DataFrame({
            "year": matches.tournament_id.str[-4:].astype(int),
            "code": matches[f"{side}_team_code"],
            "team": matches[f"{side}_team_name"],
            "match": matches.match_id, "stage": matches.stage_name,
            "gf": matches[f"{side}_team_score"], "ga": matches[f"{other}_team_score"],
            "shootout_win": matches.penalty_shootout.eq(1) &
                matches[f"{side}_team_score_penalties"].gt(matches[f"{other}_team_score_penalties"]),
        }))
    long = pd.concat(parts, ignore_index=True)
    assert not long.duplicated(["match", "code"]).any()
    long = long.assign(wins=long.gf.gt(long.ga), draws=long.gf.eq(long.ga),
                       losses=long.gf.lt(long.ga))
    aggregate = dict(games=("match", "size"), wins=("wins", "sum"),
                     draws=("draws", "sum"), losses=("losses", "sum"),
                     gf=("gf", "sum"), ga=("ga", "sum"), shootout_wins=("shootout_win", "sum"))
    annual = rates(long.groupby(["year", "code"], as_index=False).agg(**aggregate))
    assert annual.groupby("year").size().to_dict() == dict.fromkeys(YEARS, 32)
    totals = annual.groupby("year").sum(numeric_only=True)
    assert totals.games.eq(128).all() and totals.gf.eq(totals.ga).all()
    assert totals.gf.tolist() == [161, 147, 145, 171, 169, 172]
    assert totals.wins.eq(totals.losses).all()
    assert annual.games.eq(annual.wins + annual.draws + annual.losses).all()
    annual["group"] = annual.games.map({7: GROUPS[0], 5: GROUPS[1], 4: GROUPS[2], 3: GROUPS[3]})
    assert annual.groupby(["year", "group"]).size().unstack()[GROUPS].eq([4, 4, 8, 16]).all().all()
    assert annual.loc[annual.games.eq(7), ["year", "code"]].sort_values(["year", "code"]).values.tolist() == (
        podium.assign(year=podium.tournament_id.str[-4:].astype(int))
        .sort_values(["year", "team_code"])[["year", "team_code"]].values.tolist()
    )
    country = rates(long.groupby("code").agg(team=("team", "last"), **aggregate))
    country["goal_difference"] = country.gf - country.ga
    country = country.sort_values(["wins", "goal_difference", "gf", "code"],
                                  ascending=[False, False, False, True])
    country["selection_order"] = np.arange(1, len(country) + 1)
    chosen = country.head(10).copy()
    if "KOR" not in chosen.index:
        chosen = pd.concat([chosen, country.loc[["KOR"]]])
    chosen["label"] = [KO[code] for code in chosen.index]
    assert len(chosen) == 10 + int("KOR" not in country.head(10).index)
    assert chosen.index.is_unique
    ranks = pd.read_csv(DATA / "korea_positions.csv")
    korea = annual.loc[annual.code.eq("KOR")].merge(ranks, on="year", validate="one_to_one")
    assert korea.year.tolist() == YEARS
    assert korea[["games", "gf", "ga"]].sum().tolist() == [24, 28, 35]
    assert korea.wins.sum() == 7 and korea.shootout_wins.sum() == 1
    assert korea.position.between(1, 32).all()
    champions = podium.loc[podium.position.eq(1)].assign(
        year=lambda df: df.tournament_id.str[-4:].astype(int), code=lambda df: df.team_code)
    assert champions.set_index("tournament_id").team_name.to_dict() == tournaments.set_index("tournament_id").winner.to_dict()
    champions = annual.merge(champions[["year", "code"]], validate="one_to_one")
    assert len(champions) == 6 and champions.games.eq(7).all()
    group = annual.groupby("group").agg(margin=("margin", "mean"), count=("code", "size")).loc[GROUPS]

    legacy = pd.read_csv(DATA / "four_countries_from_notebook.csv")
    comparison = legacy.merge(country, left_on="Country", right_on="team", validate="one_to_one")
    assert len(comparison) == 4
    comparison["wins_with_shootout"] = comparison.wins + comparison.shootout_wins
    for old, new in [("Games", "games"), ("Wins", "wins"), ("GF", "gf"), ("GA", "ga")]:
        comparison[f"delta_{new}"] = comparison[new] - comparison[old]
    legacy_dir = DATA
    old_korea = pd.read_csv(legacy_dir / "korea_history_from_notebook.csv").set_index("연도").loc[YEARS]
    assert old_korea[["경기", "승", "무", "패", "득점", "실점"]].values.tolist() == korea[
        ["games", "wins", "draws", "losses", "gf", "ga"]
    ].values.tolist()
    position_delta = korea.position.to_numpy() - old_korea["최종순위"].to_numpy()
    assert position_delta.tolist() == [0, 0, 0, 0, -6, 0]
    old_champs = pd.read_csv(legacy_dir / "champions_from_notebook.csv")
    assert np.allclose(old_champs[["득점/경기", "실점/경기"]], champions[["scored", "conceded"]], atol=.005)
    old_groups = pd.read_csv(legacy_dir / "stage_aggregates_from_notebook.csv")
    assert old_groups["팀·대회 기록"].tolist() == group["count"].tolist()
    assert np.allclose(old_groups["득실차/경기"], group.margin, atol=.005)
    return country, chosen, korea, champions, group, comparison, annual, long

def configure_font():
    font_path = os.environ.get("KOREAN_FONT")
    windows = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts/malgun.ttf"
    if font_path or windows.is_file():
        path = font_path or windows
        font_manager.fontManager.addfont(path)
        family = font_manager.FontProperties(fname=path).get_name()
    else:
        installed = set(font_manager.get_font_names())
        family = next((name for name in ("Noto Sans CJK KR", "NanumGothic", "AppleGothic")
                       if name in installed), None)
        if family is None:
            raise RuntimeError("한글 글꼴 설치 후 KOREAN_FONT에 글꼴 파일 경로를 지정하세요.")
    plt.rcParams.update({"font.family": family, "font.size": 11, "axes.unicode_minus": False,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "text.color": "#172c41", "axes.labelcolor": "#172c41"})

def canvas(title, subtitle, xlabel, ylabel, size=(10, 5.6)):
    fig, ax = plt.subplots(figsize=size)
    fig.text(.08, .955, title, fontsize=20, weight="bold", va="top")
    fig.text(.08, .885, subtitle, fontsize=10, color=GRAY, va="top")
    ax.set(xlabel=xlabel, ylabel=ylabel)
    ax.set_axisbelow(True)
    return fig, ax

def save(fig, index, source="펠스툴 월드컵 데이터베이스", left=.16, bottom=.15, right=.95):
    fig.subplots_adjust(top=.80, bottom=bottom, left=left, right=right)
    fig.text(.08, .035, f"2002~2022년 FIFA 남자 월드컵 6개 본선  |  자료: {source}",
             fontsize=9, color=GRAY)
    fig.savefig(CHARTS / f"{FILES[index-1]}.png", dpi=300, facecolor="white")
    plt.close(fig)

def group_legend(ax):
    ax.legend(handles=[Patch(color=RED, label="대한민국"),
                       Patch(color=BLUE, label="비교 국가")], loc="lower right")

def render(chosen, korea, champions, group):
    CHARTS.mkdir(exist_ok=True)
    configure_font()
    years = korea.year.to_numpy()
    fig, ax = canvas("대한민국의 월드컵 최종 순위", "순위 숫자가 작을수록 높은 성적",
                     "대회 연도", "최종 순위 (위)")
    ax.plot(years, korea.position, "o-", color=RED, label="대한민국", linewidth=2.2)
    for year, rank in zip(years, korea.position):
        ax.annotate(f"{rank}위", (year, rank), (0, 9), textcoords="offset points", ha="center", color=RED)
    ax.set(xticks=years, ylim=(32, 0), yticks=[1, 4, 8, 12, 16, 20, 24, 28, 32])
    ax.grid(axis="y", alpha=.2)
    ax.legend(loc="lower left")
    save(fig, 1, "펠스툴 · 대회별 순위표 (README 참조)")

    y = np.arange(len(chosen))
    colors = [RED if code == "KOR" else BLUE for code in chosen.index]
    fig, ax = canvas("상위 10개국과 대한민국의 득점·실점",
                     "누적 승리 수 기준으로 선정한 국가", "경기당 득점·실점 (골)", "국가", (10, 7.7))
    a = ax.barh(y-.18, chosen.scored, .32, color=colors)
    b = ax.barh(y+.18, chosen.conceded, .32, color=colors, alpha=.40)
    for bars in [a, b]:
        ax.bar_label(bars, fmt="%.2f", padding=4)
    ax.set(yticks=y, yticklabels=chosen.label, xlim=(0, max(chosen.scored.max(), chosen.conceded.max())+.45))
    ax.invert_yaxis()
    ax.legend(handles=[Patch(color=BLUE, label="득점"), Patch(color=BLUE, alpha=.4, label="실점"),
                       Patch(color=RED, label="대한민국")], loc="lower right")
    ax.grid(axis="x", alpha=.2)
    save(fig, 2)

    fig, ax = canvas("2002년 대한민국과 역대 우승국 평균", "대한민국 7경기와 6개 대회 우승팀 42경기 비교",
                     "지표", "경기당 득점·실점 (골)")
    metrics = ["scored", "conceded"]
    for values, offset, color, label in [(korea.iloc[0][metrics], -.19, RED, "2002년 대한민국"),
                                         (champions[metrics].mean(), .19, BLUE, "6개 대회 우승국 평균")]:
        bars = ax.bar(np.arange(2)+offset, values.astype(float), .35, color=color, label=label)
        ax.bar_label(bars, fmt="%.2f", padding=4)
    ax.set(xticks=[0, 1], xticklabels=["득점", "실점"], ylim=(0, 2.65))
    ax.legend()
    ax.grid(axis="y", alpha=.2)
    save(fig, 3)

    fig, ax = canvas("최종 성적 그룹별 경기당 득실차",
                     "막대는 그룹 평균 · 빨간 점은 대한민국의 대회별 기록", "최종 성적 그룹",
                     "경기당 득실차 (골)", (11, 6.2))
    x = np.arange(4)
    bars = ax.bar(x, group.margin, .56, color=BLUE, alpha=.78, label="그룹 평균")
    for i, margin in enumerate(group.margin):
        ax.annotate(f"{margin:+.2f}", (i, margin), (-24, 8 if margin >= 0 else -8),
                    textcoords="offset points", ha="right", va="center", color=BLUE)
    for i, label in enumerate(GROUPS):
        rows = korea.loc[korea.group.eq(label)]
        offsets = np.linspace(-.32,.32,len(rows)) if len(rows)>1 else [0]
        for j, (offset, row) in enumerate(zip(offsets, rows.itertuples())):
            ax.scatter(i+offset, row.margin, color=RED, zorder=4)
            ax.annotate(f"{row.year}년\n{row.margin:+.2f}", (i+offset, row.margin),
                        (0, 8 if j%2==0 else -25), textcoords="offset points",
                        ha="center", fontsize=8, color=RED,
                        bbox={"facecolor":"white","edgecolor":"none","alpha":.94,"pad":1.3})
    ax.set(xticks=x, xticklabels=[f"{label}\n({n}건)" for label,n in zip(GROUPS,group['count'])], ylim=(-1.65,1.55))
    ax.axhline(0, color=GRAY, linewidth=1)
    ax.legend(handles=[Patch(color=BLUE,label="그룹 평균"),Patch(color=RED,label="대한민국")])
    save(fig, 4, bottom=.18)

    fig, ax = canvas("상위 10개국과 대한민국의 승률", "연장 종료 때 동점이면 무승부 · 승부차기 제외",
                     "승률 (%)", "국가", (10, 7.4))
    bars = ax.barh(y, chosen.win_rate, color=colors)
    ax.bar_label(bars, labels=[f"{r.win_rate:.1f}%  ({r.wins}승/{r.games}경기)"
                               for r in chosen.itertuples()], padding=5)
    ax.set(yticks=y, yticklabels=chosen.label, xlim=(0,100))
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=.2)
    group_legend(ax)
    save(fig, 5)

    fig, ax = canvas("상위 10개국과 대한민국의 공격·수비", "오른쪽일수록 득점이 많고 아래쪽일수록 실점이 적음",
                     "경기당 득점 (골)", "경기당 실점 (골)", (12, 7))
    # 번호를 좌표와 연결해 가까운 국가의 긴 이름이 겹치지 않도록 한다.
    for i, (row, color) in enumerate(zip(chosen.itertuples(), colors), 1):
        ax.scatter(row.scored, row.conceded, color=color, s=370, edgecolor="white", zorder=3)
        ax.text(row.scored,row.conceded,str(i),ha="center",va="center",color="white",fontsize=8,zorder=4)
        fig.text(.76,.765-(i-1)*.049,f"{i:02d}  {row.label}  {row.scored:.2f} / {row.conceded:.2f}",
                 color=color, fontsize=10)
    ax.margins(.10)
    ax.grid(alpha=.22)
    group_legend(ax)
    save(fig, 6, left=.10, right=.72)

    labels = ["최종 순위", "승률", "경기당 득점", "경기당 실점"]
    corr = korea[["position", "win_rate", "scored", "conceded"]].corr()
    fig, ax = canvas("대한민국의 대회별 상관관계", "6개 대회 기준 · 순위 숫자가 클수록 낮은 성적",
                     "비교 지표", "비교 지표", (8.8, 6.2))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set(xticks=range(4), yticks=range(4), xticklabels=labels, yticklabels=labels)
    for i in range(4):
        for j in range(4):
            value = corr.iat[i,j]
            ax.text(j,i,f"{value:+.2f}",ha="center",va="center",
                    color="white" if abs(value)>.65 else "#172c41")
    fig.colorbar(im, ax=ax, shrink=.8, label="피어슨 상관계수 (무단위)")
    fig.legend(handles=[Patch(color=RED,label="대한민국 표본")], loc="upper right", bbox_to_anchor=(.96,.88))
    save(fig, 7, "펠스툴 · 대회별 순위표 (README 참조)", left=.19)

    fig, ax = canvas("대한민국의 대회별 득점·실점 분포", "점 하나는 한 대회의 경기당 평균 · 상자는 가운데 50%",
                     "지표", "대회별 경기당 평균 (골)")
    vals = [korea.scored, korea.conceded]
    ax.boxplot(vals, widths=.38, patch_artist=True,
               boxprops={"facecolor":"#fae3e7","edgecolor":RED},
               medianprops={"color":RED,"linewidth":2}, showfliers=False)
    for i, values in enumerate(vals, 1):
        ax.scatter(i+np.linspace(-.12,.12,6),values,color=RED,s=25,zorder=3)
        ax.text(i+.24,values.median(),f"중앙값 {values.median():.2f}",va="center",color=RED)
    ax.set(xticks=[1,2],xticklabels=["득점","실점"],xlim=(.55,2.72),ylim=(.6,2.22))
    ax.grid(axis="y",alpha=.2)
    ax.legend(handles=[Patch(color=RED,label="대한민국")],loc="upper left")
    save(fig, 8)

def main():
    country, chosen, korea, champions, group, comparison, annual, long = analyze()
    for name, frame in [("country_summary", country), ("top10_comparison", chosen),
                        ("korea_summary", korea.set_index("year")), ("champion_summary", champions.set_index("year")),
                        ("stage_summary", group), ("legacy_comparison", comparison.set_index("Country"))]:
        frame.to_csv(DATA / f"{name}.csv", encoding="utf-8-sig")
    render(chosen, korea, champions, group)
    print("Independent score cross-check: 384/384.")
    print("Legacy cross-check: annual Korea totals, champion averages and stage aggregates passed.")
    print(f"Validated {len(long)//2} matches, {len(annual)} team-editions, {len(country)} teams.")
    print(chosen[["games","wins","scored","conceded","win_rate"]].round(3).to_string())
    print(comparison[["Country","Wins","wins","shootout_wins","delta_games","delta_gf","delta_ga"]].to_string(index=False))

if __name__ == "__main__":
    main()


