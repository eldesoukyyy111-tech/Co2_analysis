"""
Who Pollutes the Most? CO2 Emissions vs Wealth (1990 - latest)
Data: Our World in Data - CO2 and Greenhouse Gas Emissions
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")

df = pd.read_csv("owid-co2-data.csv")
print("Original shape:", df.shape)

df = df[df["iso_code"].notna()]
df = df[~df["iso_code"].str.startswith("OWID")]


df = df[df["year"] >= 1990]


cols = [
    "country",
    "year",
    "population",
    "gdp",
    "co2",
    "co2_per_capita",
    "coal_co2",
    "oil_co2",
    "gas_co2",
]
df = df[cols]

print("\nMissing values before dropping:")
print(df.isna().sum())

df_co2 = df.dropna(subset=["co2", "co2_per_capita"])
df_gdp = df.dropna(subset=["gdp", "co2", "co2_per_capita", "population"])


def last_complete_year(data):
    """Latest year that has data for at least 100 countries."""
    counts = data.groupby("year")["country"].nunique()
    return counts[counts >= 100].index.max()


co2_year = last_complete_year(df_co2)
gdp_year = last_complete_year(df_gdp)

print("\nLatest year for CO2 analysis:", co2_year)
print("Latest year for GDP analysis:", gdp_year)
print("Shape (CO2 data):", df_co2.shape)
print("Shape (GDP data):", df_gdp.shape)
print(df_co2.head())

latest_co2 = df_co2[df_co2["year"] == co2_year]
latest_gdp = df_gdp[df_gdp["year"] == gdp_year].copy()

print("\nColumn statistics:")
print(df_co2[["population", "co2", "co2_per_capita"]].describe())

top_total = latest_co2.nlargest(10, "co2")

plt.figure(figsize=(10, 6))
sns.barplot(data=top_total, x="co2", y="country", color="firebrick")
plt.title(f"Top 10 Countries by CO2 Emissions ({co2_year})")
plt.xlabel("CO2 (million tonnes)")
plt.ylabel("")
plt.tight_layout()
plt.savefig("01_top10_total_co2.png", dpi=150)
plt.show()

big_countries = latest_co2[latest_co2["population"] > 1_000_000]
top_per_capita = big_countries.nlargest(10, "co2_per_capita")

plt.figure(figsize=(10, 6))
sns.barplot(data=top_per_capita, x="co2_per_capita", y="country", color="darkorange")
plt.title(f"Top 10 Countries by CO2 per Capita ({co2_year}, population > 1M)")
plt.xlabel("CO2 per capita (tonnes per person)")
plt.ylabel("")
plt.tight_layout()
plt.savefig("02_top10_per_capita.png", dpi=150)
plt.show()

trend_data = df_co2[df_co2["year"] <= co2_year]
world_trend = trend_data.groupby("year")["co2"].sum().reset_index()

plt.figure(figsize=(10, 6))
sns.lineplot(data=world_trend, x="year", y="co2", linewidth=2.5, color="black")
plt.title(f"Total CO2 Emissions Over Time (sum of countries, 1990-{co2_year})")
plt.xlabel("Year")
plt.ylabel("CO2 (million tonnes)")
plt.tight_layout()
plt.savefig("03_world_trend.png", dpi=150)
plt.show()

latest_gdp["gdp_per_capita"] = latest_gdp["gdp"] / latest_gdp["population"]

plt.figure(figsize=(10, 7))
sns.scatterplot(
    data=latest_gdp,
    x="gdp_per_capita",
    y="co2_per_capita",
    size="population",
    sizes=(20, 600),
    alpha=0.6,
    legend=False,
)
plt.xscale("log")
plt.title(f"GDP per Capita vs CO2 per Capita ({gdp_year})")
plt.xlabel("GDP per capita (log scale)")
plt.ylabel("CO2 per capita (tonnes)")

for _, row in latest_gdp.nlargest(8, "co2").iterrows():
    plt.text(row["gdp_per_capita"], row["co2_per_capita"], row["country"], fontsize=9)

plt.tight_layout()
plt.savefig("04_gdp_vs_co2.png", dpi=150)
plt.show()

corr = latest_gdp[
    ["population", "gdp", "co2", "co2_per_capita", "coal_co2", "oil_co2", "gas_co2"]
].corr()

plt.figure(figsize=(9, 7))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1)
plt.title(f"Correlation Heatmap ({gdp_year})")
plt.tight_layout()
plt.savefig("05_correlation.png", dpi=150)
plt.show()


top5 = top_total["country"].head(5).tolist()
fuel = (
    latest_co2[latest_co2["country"].isin(top5)]
    .set_index("country")[["coal_co2", "oil_co2", "gas_co2"]]
    .fillna(0)
    .loc[top5]
)

fuel.plot(
    kind="bar", stacked=True, figsize=(10, 6), color=["#444444", "#c0392b", "#2980b9"]
)
plt.title(f"CO2 by Fuel Source - Top 5 Emitters ({co2_year})")
plt.xlabel("")
plt.ylabel("CO2 (million tonnes)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("06_fuel_mix.png", dpi=150)
plt.show()


start_year = 2000
gdp_wide = df_gdp.pivot(index="country", columns="year", values="gdp")
co2_wide = df_gdp.pivot(index="country", columns="year", values="co2")

common = gdp_wide.index.intersection(co2_wide.index)
result = pd.DataFrame(
    {
        "gdp_change_pct": (
            gdp_wide.loc[common, gdp_year] / gdp_wide.loc[common, start_year] - 1
        )
        * 100,
        "co2_change_pct": (
            co2_wide.loc[common, gdp_year] / co2_wide.loc[common, start_year] - 1
        )
        * 100,
        "co2_start": co2_wide.loc[common, start_year],
    }
).dropna()

result = result[result["co2_start"] > 10]

decoupled_all = result[(result["gdp_change_pct"] > 0) & (result["co2_change_pct"] < 0)]
decoupled_top = decoupled_all.sort_values("co2_change_pct").head(10).reset_index()

print(f"\nTop 10 countries where GDP grew and CO2 fell ({start_year} -> {gdp_year}):")
print(decoupled_top)
print(f"\nNumber of countries that achieved this: {len(decoupled_all)} out of {len(result)}")

plt.figure(figsize=(10, 6))
sns.scatterplot(data=result, x="gdp_change_pct", y="co2_change_pct", alpha=0.7)
plt.axhline(0, color="black", linewidth=1)
plt.title(f"GDP Growth vs CO2 Change ({start_year} to {gdp_year})")
plt.xlabel("GDP change (%)")
plt.ylabel("CO2 change (%)")
plt.tight_layout()
plt.savefig("07_decoupling.png", dpi=150)
plt.show()

# =====================================================
# 11) Conclusions (fill in after looking at your results)
# =====================================================

# 1. The largest total emitter is China.

# 2. The highest per-capita emitters is Qatar.

# 3. Is wealth linked to emissions? Yes, there is a moderate positive correlation between wealth (GDP per capita) and CO2 emissions per capita. Richer countries generally emit more CO2 per person,but the relationship is not perfect.

# 4. Number of countries that decoupled growth from emissions = 35 out of 91

# Note: correlation does not imply causation.
# Note: GDP data ends in the GDP year, CO2 data goes further.
