# Data dictionary

Each row in county_year_audit.csv represents one supplied Zillow county and calendar year, 2015–2025. housing_affordability.csv contains eligible 2015–2024 rows only. FIPS must be imported as text.

| Field | Meaning |
|---|---|
| county_fips | Five-character state + county identifier; leading zeros preserved |
| county, state | Zillow county label and postal state code |
| year | Calendar year, integer |
| home_value | Nominal USD; mean of available monthly Zillow ZHVI values; use only when housing_eligible |
| months_available | Count of nonmissing monthly housing observations, 0–12 |
| housing_eligible | True only when months_available = 12 |
| median_household_income | Annual Census SAIPE estimate, nominal USD; missing in 2025 |
| income_lower, income_upper | Published 90% income confidence limits, USD |
| census_county, census_state | Census labels for audit of geographic joins |
| income_eligible | Positive income estimate and lower limit |
| avg_mortgage_rate | Arithmetic average of weekly FRED observations; percent, e.g. 6.72 |
| rate_observations | Weekly observations used in annual average |
| eligible | Housing and income eligibility both true |
| balanced_panel | County has ten eligible years in 2015–2024; false for 2025 |
| monthly_payment | Modeled USD monthly principal & interest; use only with housing_eligible |
| price_to_income_ratio | Home value / annual median household income; use eligible rows |
| payment_to_income_ratio | 12 × monthly payment / annual median household income, decimal |
| burden_income_lower_bound | 12 × payment / upper income limit, decimal; income-only sensitivity |
| burden_income_upper_bound | 12 × payment / lower income limit, decimal; income-only sensitivity |
| home_value_yoy_growth | Decimal annual change; missing unless consecutive housing years eligible |
| income_yoy_growth | Decimal annual income change; no filling missing years |

County changes use the consistent 2015–2024 panel. *_growth fields are decimal cumulative changes. burden_change_pp and *_contribution_pp are percentage points. Summary medians are computed separately: do not divide median payment by median income to reproduce the median burden. Null values mean unavailable, never zero.
