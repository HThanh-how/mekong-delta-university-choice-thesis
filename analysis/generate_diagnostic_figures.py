"""Generate publication-quality diagnostic figures from the survey data."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
DATA = pd.read_csv(ROOT / "data" / "survey_486.csv", encoding="utf-8-sig")
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)

FACTORS = ["FIT", "CAR", "REP", "COS", "SOC", "COM", "LOC", "DEC"]
PREDICTORS = FACTORS[:-1]
SCORES = pd.DataFrame(
    {factor: DATA[[f"{factor}{i}" for i in range(1, 5)]].mean(axis=1) for factor in FACTORS}
)
COLORS = ["#145DA0", "#2A9D8F", "#F4A261", "#E9C46A", "#E76F51", "#4F5D95", "#65B5D8", "#6C757D"]

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "figure.dpi": 160,
})


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(OUT / name, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# Correlation matrix.
corr = SCORES.corr()
fig, ax = plt.subplots(figsize=(7.4, 6.1))
im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(FACTORS)), FACTORS)
ax.set_yticks(range(len(FACTORS)), FACTORS)
for i in range(len(FACTORS)):
    for j in range(len(FACTORS)):
        ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", color="black")
fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Hệ số tương quan Pearson")
ax.set_title("Ma trận tương quan giữa các thang đo")
save(fig, "correlation-matrix.png")


# Regression and diagnostic quantities.
x = sm.add_constant(SCORES[PREDICTORS])
model = sm.OLS(SCORES["DEC"], x).fit()
influence = model.get_influence()
std_resid = influence.resid_studentized_internal
cooks = influence.cooks_distance[0]
fitted = model.fittedvalues.to_numpy()

fig, axes = plt.subplots(2, 2, figsize=(9.2, 7.2))
ax = axes[0, 0]
ax.hist(std_resid, bins=18, density=True, color=COLORS[0], alpha=.82, edgecolor="white")
grid = np.linspace(std_resid.min(), std_resid.max(), 200)
ax.plot(grid, stats.norm.pdf(grid), color=COLORS[4], linewidth=1.8)
ax.set(title="Phân phối phần dư chuẩn hóa", xlabel="Phần dư chuẩn hóa", ylabel="Mật độ")

ax = axes[0, 1]
(osm, osr), (slope, intercept, _) = stats.probplot(std_resid, dist="norm")
ax.scatter(osm, osr, s=13, color=COLORS[1], alpha=.7)
ax.plot(osm, slope * np.asarray(osm) + intercept, color=COLORS[4], linewidth=1.5)
ax.set(title="Biểu đồ Q--Q của phần dư", xlabel="Phân vị lý thuyết", ylabel="Phân vị quan sát")

ax = axes[1, 0]
ax.scatter(fitted, std_resid, s=14, color=COLORS[5], alpha=.55)
ax.axhline(0, color=COLORS[4], linewidth=1.2)
ax.axhline(2, color="grey", linestyle="--", linewidth=.8)
ax.axhline(-2, color="grey", linestyle="--", linewidth=.8)
ax.set(title="Phần dư theo giá trị dự báo", xlabel="Giá trị DEC dự báo", ylabel="Phần dư chuẩn hóa")

ax = axes[1, 1]
ax.vlines(np.arange(1, len(cooks) + 1), 0, cooks, color=COLORS[2], linewidth=.7)
ax.axhline(4 / len(cooks), color=COLORS[4], linestyle="--", linewidth=1, label="Ngưỡng 4/n")
ax.set(title="Khoảng cách Cook", xlabel="Số thứ tự quan sát", ylabel="Cook's Distance")
ax.legend(frameon=False, fontsize=8)
fig.tight_layout()
save(fig, "regression-diagnostics.png")


# Item means.
items = [f"{factor}{i}" for factor in FACTORS for i in range(1, 5)]
item_means = DATA[items].mean()
item_colors = [COLORS[index // 4] for index in range(len(items))]
fig, ax = plt.subplots(figsize=(8.4, 8.5))
y = np.arange(len(items))
ax.barh(y, item_means, color=item_colors, edgecolor="white")
ax.set_yticks(y, items)
ax.invert_yaxis()
ax.set_xlim(1, 5)
ax.set_xlabel("Điểm trung bình (1--5)")
ax.set_title("Điểm trung bình của 32 biến quan sát")
ax.grid(axis="x", alpha=.25)
for pos, value in zip(y, item_means):
    ax.text(value + .04, pos, f"{value:.2f}", va="center", fontsize=7.5)
save(fig, "item-means.png")


# Stacked response distributions by construct.
distribution = []
for factor in FACTORS:
    values = DATA[[f"{factor}{i}" for i in range(1, 5)]].to_numpy().ravel()
    distribution.append([100 * np.mean(values == level) for level in range(1, 6)])
distribution = np.asarray(distribution)
likert_colors = ["#D73027", "#FC8D59", "#FEE08B", "#91CF60", "#1A9850"]
fig, ax = plt.subplots(figsize=(8.4, 5.2))
left = np.zeros(len(FACTORS))
for level in range(5):
    ax.barh(FACTORS, distribution[:, level], left=left, color=likert_colors[level], label=str(level + 1))
    left += distribution[:, level]
ax.set_xlim(0, 100)
ax.set_xlabel("Tỷ lệ phản hồi (%)")
ax.set_title("Phân bố mức trả lời theo thang đo")
ax.legend(title="Mức Likert", ncol=5, loc="lower center", bbox_to_anchor=(.5, -0.27), frameon=False)
save(fig, "likert-distribution.png")


# Group comparisons.
fig, axes = plt.subplots(1, 3, figsize=(10.2, 4.6))
area = [SCORES.loc[DATA.KhuVuc == code, "LOC"] for code in [0, 1]]
income = [SCORES.loc[DATA.ThuNhap == code, "COS"] for code in [1, 2, 3]]
gender = [SCORES.loc[DATA.GioiTinh == code, "DEC"] for code in [1, 2, 3]]
specs = [
    (area, ["Thành thị", "Nông thôn"], "LOC theo khu vực"),
    (income, ["<10", "10--20", ">20"], "COS theo thu nhập (triệu đồng)"),
    (gender, ["Nam", "Nữ", "Khác"], "DEC theo giới tính"),
]
for ax, (groups, labels, title), color in zip(axes, specs, COLORS[:3]):
    bp = ax.boxplot(groups, tick_labels=labels, patch_artist=True, widths=.58, showmeans=True)
    for patch in bp["boxes"]:
        patch.set_facecolor(color)
        patch.set_alpha(.68)
    ax.set_title(title)
    ax.set_ylim(1, 5.1)
    ax.grid(axis="y", alpha=.22)
fig.tight_layout()
save(fig, "group-comparisons.png")

print(f"Generated figures in {OUT}")
