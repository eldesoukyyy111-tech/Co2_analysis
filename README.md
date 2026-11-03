# Who Pollutes the Most? CO2 Emissions vs Wealth

Exploratory analysis of global CO2 emissions (1990–latest) using the Our World in Data dataset.

## Questions answered
- Which countries emit the most CO2 in total and per person?
- Is wealth linked to emissions?
- Which countries grew their economy while cutting emissions?

## Key findings
- Largest total emitter: China
- Highest per-capita emitter: Qatar
- Moderate positive correlation between GDP per capita and CO2 per capita
- 35 of 91 countries decoupled GDP growth from CO2 emissions (2000 → latest year)

## Charts
Top 10 total emitters, top 10 per capita, global trend, GDP vs CO2, correlation heatmap, fuel mix, decoupling scatter.

## How to run
1. Install the libraries: pip install pandas numpy matplotlib seaborn
2. Download owid-co2-data.csv from https://github.com/owid/co2-data and put it next to the script.
3. Run: python Co2_analysis.py

## Notes
- Correlation does not imply causation.
- GDP data ends earlier than CO2 data.
- Data source: Our World in Data.
