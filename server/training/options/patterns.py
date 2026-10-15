import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ── Load & parse ──────────────────────────────────────────────────────────────
df = pd.read_csv("./spx_hist.csv")
df.columns = df.columns.str.strip()
df["Date"] = pd.to_datetime(df["Date"].str.strip())
df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
df = df.dropna(subset=["Close"]).sort_values("Date")

df["Year"]    = df["Date"].dt.year
df["Quarter"] = df["Date"].dt.quarter
df["Month"]   = df["Date"].dt.month
df["Weekday"] = df["Date"].dt.dayofweek   # 0=Mon … 4=Fri

# ── Averages ──────────────────────────────────────────────────────────────────
avg_year    = df.groupby("Year")["Close"].mean()
avg_quarter = df.groupby("Quarter")["Close"].mean()
avg_month   = df.groupby("Month")["Close"].mean()
avg_weekday = df.groupby("Weekday")["Close"].mean()

# ── Labels ────────────────────────────────────────────────────────────────────
quarter_labels = ["Q1\n(Jan–Mar)", "Q2\n(Apr–Jun)", "Q3\n(Jul–Sep)", "Q4\n(Oct–Dec)"]
month_labels   = ["Jan","Feb","Mar","Apr","May","Jun",
                  "Jul","Aug","Sep","Oct","Nov","Dec"]
weekday_labels = ["Mon","Tue","Wed","Thu","Fri"]

# ── Colour helpers ────────────────────────────────────────────────────────────
def bar_colors(values, low_color="#e74c3c", high_color="#2ecc71", mid_color="#95a5a6"):
    mn, mx = values.min(), values.max()
    colors = []
    for v in values:
        if v == mn:
            colors.append(low_color)
        elif v == mx:
            colors.append(high_color)
        else:
            colors.append(mid_color)
    return colors

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(16, 11))
fig.suptitle("S&P 500 – Average Close Price by Period  (2020–2025)",
             fontsize=16, fontweight="bold", y=1.01)
fig.patch.set_facecolor("#1a1a2e")

PANEL_BG   = "#16213e"
TICK_COLOR = "#c8d6e5"
GRID_COLOR = "#2c3e50"
TEXT_COLOR = "#ecf0f1"

def style_ax(ax, title):
    ax.set_facecolor(PANEL_BG)
    ax.set_title(title, color=TEXT_COLOR, fontsize=13, fontweight="bold", pad=10)
    ax.tick_params(colors=TICK_COLOR, labelsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.set_ylabel("Avg Close (USD)", color=TICK_COLOR, fontsize=10)
    ax.grid(axis="y", color=GRID_COLOR, linestyle="--", linewidth=0.6, alpha=0.7)
    ax.spines[:].set_visible(False)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color(TICK_COLOR)

def annotate_bars(ax, bars, values):
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.01,
                f"{val:,.0f}",
                ha="center", va="bottom", fontsize=8.5, color=TEXT_COLOR)

# ── 1. By Year ────────────────────────────────────────────────────────────────
ax1 = axes[0, 0]
cols = bar_colors(avg_year)
b = ax1.bar(avg_year.index.astype(str), avg_year.values, color=cols, edgecolor="none", width=0.6)
style_ax(ax1, "Average Close by Year")
ax1.set_xlabel("Year", color=TICK_COLOR, fontsize=10)
annotate_bars(ax1, b, avg_year.values)

# ── 2. By Quarter ─────────────────────────────────────────────────────────────
ax2 = axes[0, 1]
cols = bar_colors(avg_quarter)
b = ax2.bar(quarter_labels, avg_quarter.values, color=cols, edgecolor="none", width=0.5)
style_ax(ax2, "Average Close by Quarter")
ax2.set_xlabel("Quarter", color=TICK_COLOR, fontsize=10)
annotate_bars(ax2, b, avg_quarter.values)

# ── 3. By Month ───────────────────────────────────────────────────────────────
ax3 = axes[1, 0]
cols = bar_colors(avg_month)
b = ax3.bar(month_labels, avg_month.values, color=cols, edgecolor="none", width=0.6)
style_ax(ax3, "Average Close by Month")
ax3.set_xlabel("Month", color=TICK_COLOR, fontsize=10)
annotate_bars(ax3, b, avg_month.values)

# ── 4. By Day of Week ─────────────────────────────────────────────────────────
ax4 = axes[1, 1]
cols = bar_colors(avg_weekday)
b = ax4.bar(weekday_labels, avg_weekday.values, color=cols, edgecolor="none", width=0.5)
style_ax(ax4, "Average Close by Day of Week")
ax4.set_xlabel("Day", color=TICK_COLOR, fontsize=10)
annotate_bars(ax4, b, avg_weekday.values)

# ── Legend note ───────────────────────────────────────────────────────────────
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor="#2ecc71", label="Highest avg"),
                   Patch(facecolor="#e74c3c", label="Lowest avg"),
                   Patch(facecolor="#95a5a6", label="All others")]
fig.legend(handles=legend_elements, loc="lower center", ncol=3,
           frameon=False, fontsize=10,
           labelcolor=TEXT_COLOR, facecolor=PANEL_BG,
           bbox_to_anchor=(0.5, -0.04))

plt.tight_layout()
plt.savefig("./spx_seasonality.png",
            dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())