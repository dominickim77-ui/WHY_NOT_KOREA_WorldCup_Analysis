"""Build three charts from numeric tables saved in the original notebook."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "WHY_NOT_KOREA_WorldCup_Analysis.ipynb"


def saved_table(cells, index):
    return next(
        "".join(output["data"]["text/plain"])
        for output in cells[index]["outputs"]
        if "text/plain" in output.get("data", {})
    )


def save(fig, filename):
    fig.savefig(ROOT / "charts" / filename, dpi=170, bbox_inches="tight")
    plt.close(fig)


def main():
    cells = json.loads(NOTEBOOK.read_text(encoding="utf-8"))["cells"]
    history_rows = [line.split()[1:] for line in saved_table(cells, 5).splitlines()[1:]]
    korea = pd.DataFrame(
        history_rows, columns=["Year", "Rank", "Games", "Wins", "Draws", "Losses", "GF", "GA"]
    ).astype(int).query("2002 <= Year <= 2022")
    assert len(korea) == 6 and korea["Year"].is_unique
    assert (korea["Games"] > 0).all()
    assert korea["Games"].eq(korea["Wins"] + korea["Draws"] + korea["Losses"]).all()

    summary_text = saved_table(cells, 8).split("Conceded Per Game")[0]
    records = []
    for line in summary_text.rstrip().splitlines()[2:]:
        country, games, wins, gf, ga, _, _ = line.rsplit(maxsplit=6)
        records.append((country.strip(), int(games), int(wins), int(gf), int(ga)))
    totals = pd.DataFrame(records, columns=["Country", "Games", "Wins", "GF", "GA"])
    assert len(totals) == 4 and totals["Country"].is_unique
    assert (totals["Games"] > 0).all()
    assert totals.set_index("Country").loc["South Korea", ["Games", "Wins", "GF", "GA"]].equals(
        korea[["Games", "Wins", "GF", "GA"]].sum().rename("South Korea")
    )

    fig, ax = plt.subplots(figsize=(8, 5), layout="constrained")
    for row in totals.itertuples(index=False):
        x, y = row.GF / row.Games, row.GA / row.Games
        ax.scatter(x, y, s=75, color="#bc3245" if row.Country == "South Korea" else "#176e88")
        ax.annotate(row.Country, (x, y), xytext=(7, 7), textcoords="offset points")
    ax.set(xlabel="Goals scored per game", ylabel="Goals conceded per game",
           title="Scoring vs conceding | Four countries, 2002-2022")
    ax.margins(x=0.17, y=0.18)
    ax.grid(alpha=0.25)
    save(fig, "06_country_scatter.png")

    metrics = pd.DataFrame({
        "Final rank": korea["Rank"],
        "Win rate": korea["Wins"] / korea["Games"],
        "Goals scored/game": korea["GF"] / korea["Games"],
        "Goals conceded/game": korea["GA"] / korea["Games"],
    })
    corr = metrics.corr(method="pearson")
    fig, ax = plt.subplots(figsize=(8, 6), layout="constrained")
    image = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr)), corr.columns, rotation=25, ha="right")
    ax.set_yticks(range(len(corr)), corr.index)
    for row, values in enumerate(corr.to_numpy()):
        for col, value in enumerate(values):
            ax.text(col, row, f"{value:.2f}", ha="center", va="center",
                    color="white" if abs(value) > 0.65 else "#172536")
    ax.set_title("South Korea | Pearson correlation, 2002-2022 (n=6 editions)")
    fig.colorbar(image, ax=ax, shrink=0.8, label="Pearson r")
    save(fig, "07_korea_correlation_heatmap.png")

    fig, ax = plt.subplots(figsize=(7, 5), layout="constrained")
    distributions = [metrics["Goals scored/game"], metrics["Goals conceded/game"]]
    ax.boxplot(distributions, showfliers=False, patch_artist=True,
               boxprops={"facecolor": "#c7e3eb"}, medianprops={"color": "#bc3245", "linewidth": 2})
    offsets = [-0.075, -0.045, -0.015, 0.015, 0.045, 0.075]
    for position, values in enumerate(distributions, start=1):
        ax.scatter([position + offset for offset in offsets], values, s=28,
                   color="#176e88", zorder=3)
    ax.set_xticks([1, 2], ["Scored", "Conceded"])
    ax.set(ylabel="Goals per game", title="South Korea | Goal distributions, 2002-2022 (n=6 editions)")
    ax.grid(axis="y", alpha=0.25)
    save(fig, "08_korea_goals_boxplot.png")

    print(corr.round(3).to_string())
    print(metrics.median().to_string())


if __name__ == "__main__":
    main()

