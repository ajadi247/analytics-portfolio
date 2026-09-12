# Tableau dashboard specification

Connect Tableau to ../data/processed/housing_affordability.csv. Set county_fips to String and geographic role County; include state to disambiguate. This is a Tableau-ready dataset, not a published native Tableau workbook.

1. Add Year, State and County filters. Format payment_to_income_ratio as Percentage.
2. County map: geographic county or FIPS plus state, colored by payment_to_income_ratio. Filter to one year; do not sum ratios. Use MIN for each county-year and show income limits in the tooltip.
3. Trend: year on Columns, MEDIAN(payment_to_income_ratio) on Rows. Filter balanced_panel=True. Preserve the fixed panel when comparing years.
4. KPI cards: MEDIAN(home_value), MEDIAN(median_household_income), MEDIAN(monthly_payment), MEDIAN(payment_to_income_ratio). Label them county medians, not U.S. household statistics.
5. Ranking: county and state, sorted by payment_to_income_ratio for a single year. State that income uncertainty is not used for significance ranking.
6. Import county_changes_2015_2024.csv separately for price/rate/income contribution bars. Use AVG of each contribution in percentage points. Do not average duplicated county values after an unchecked join.

Dashboard size: 1280 × 900, responsive layouts if publishing. Use navy/teal for values and orange for income. Keep costs excluded and panel definitions visible. The supplied web dashboard provides the interactive portfolio deliverable for this release.
