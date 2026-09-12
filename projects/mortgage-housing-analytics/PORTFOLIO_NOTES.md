# Portfolio notes and learning guide

## Suggested project description
Developed an AI-assisted county-level housing affordability case study combining Zillow home values, Census annual income estimates and Freddie Mac mortgage rates. The reproducible Python and SQLite workflow audits 33,781 county-year records and analyzes 2,486 consistently observed counties.

## Resume bullet to adapt after reviewing the work
- Built and validated a housing affordability analysis using Python and SQL, integrating three public data sources and decomposing modeled payment-burden changes into home-value, rate and income contributions.

Use this wording only to the extent it accurately describes your participation and understanding. Do not claim to have built a native Tableau workbook; this release provides Tableau-ready data and instructions.

## Interview talking points
- Why annual SAIPE? It provides single-year county estimates, including smaller counties; ACS five-year estimates overlap.
- Why a balanced panel? Adding counties over time can change a median even without a within-county change.
- Why FIPS? Names repeat and geography changes. Connecticut's unmatched legacy codes were audited rather than forced into a join.
- Why principal and interest? It is comparable and transparent, but incomplete as a total cost measure.
- Why decomposition? It assigns interaction effects across six orders; it is not causal inference.
- What would you improve? Verify Zillow series metadata, harmonize boundaries, add ownership costs and weights, and examine uncertainty.

## Rebuild together in six sessions
1. Inspect the original CSV, dates, FIPS and missingness. Explain each pandas operation.
2. Reshape monthly data, count observations and compare 10/11/12-month rules.
3. Parse one Census record, join by FIPS-year and investigate unmatched records.
4. Build the mortgage formula by hand; reconcile the final balance.
5. Reproduce SQL medians and growth comparisons; explain mean versus median.
6. Rebuild dashboard views and explain three findings with limitations.
