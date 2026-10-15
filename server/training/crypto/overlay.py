import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ── Load & parse ──────────────────────────────────────────────────────────────
df = pd.read_csv("data/bitcoin.csv")   # update path if needed
df.columns = df.columns.str.strip()
df["Date"]  = pd.to_datetime(df["Date"].str.strip())
df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
df = df.dropna(subset=["Close"]).sort_values("Date").reset_index(drop=True)
df["Year"]      = df["Date"].dt.year
df["DayOfYear"] = df["Date"].dt.dayofyear

years = sorted(df["Year"].unique())

COLORS = ["#e74c3c","#f39c12","#2ecc71","#3498db","#9b59b6","#1abc9c"]

fig, ax = plt.subplots(figsize=(16, 8))
fig.patch.set_facecolor("#1a1a2e")
ax.set_facecolor("#16213e")

for i, year in enumerate(years):
    ydf = df[df["Year"] == year].sort_values("DayOfYear").copy()
    base = ydf["Close"].iloc[0]
    ydf["Norm"] = (ydf["Close"] / base) * 100
    color = COLORS[i % len(COLORS)]
    lw = 2.5 if year == years[-1] else 1.8
    ax.plot(ydf["DayOfYear"], ydf["Norm"], color=color, linewidth=lw, alpha=0.9, label=str(year))
    last = ydf.iloc[-1]
    ax.annotate(f"{year}  {last['Norm']:.1f}",
                xy=(last["DayOfYear"], last["Norm"]),
                xytext=(4, 0), textcoords="offset points",
                color=color, fontsize=9, va="center", fontweight="bold")

ax.axhline(100, color="#ffffff", linewidth=0.7, linestyle="--", alpha=0.3)

month_starts = [1,32,60,91,121,152,182,213,244,274,305,335]
month_labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
ax.set_xticks(month_starts)
ax.set_xticklabels(month_labels, fontsize=10)
ax.set_xlim(1, 366)

TICK_COLOR = "#c8d6e5"
GRID_COLOR = "#2c3e50"
TEXT_COLOR = "#ecf0f1"

ax.set_title("S&P 500 – Annual Close Price Overlay  (indexed to 100 at Jan 1 each year)",
             color=TEXT_COLOR, fontsize=14, fontweight="bold", pad=14)
ax.set_ylabel("Indexed Price  (Jan 1 = 100)", color=TICK_COLOR, fontsize=11)
ax.set_xlabel("Month", color=TICK_COLOR, fontsize=11)
ax.tick_params(colors=TICK_COLOR)
for lbl in ax.get_xticklabels() + ax.get_yticklabels():
    lbl.set_color(TICK_COLOR)
ax.grid(axis="both", color=GRID_COLOR, linestyle="--", linewidth=0.5, alpha=0.6)
ax.spines[:].set_visible(False)
ax.legend(loc="upper left", frameon=True, framealpha=0.2,
          facecolor="#1a1a2e", edgecolor="#2c3e50", fontsize=10, labelcolor=TEXT_COLOR)

plt.tight_layout()
plt.savefig("spx_yearly_overlay.png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.show()