-- SQLite queries. Open housing.sqlite and execute each query separately.
-- 1. Coverage and exclusions: all county-years, including failed joins.
SELECT year, COUNT(*) AS candidate_county_years, SUM(eligible) AS eligible_counties,
       SUM(balanced_panel) AS panel_counties
FROM county_year GROUP BY year ORDER BY year;

-- 2. Consistent-panel medians via a window function, including even samples.
WITH ordered AS (
 SELECT year, payment_to_income_ratio,
 ROW_NUMBER() OVER (PARTITION BY year ORDER BY payment_to_income_ratio) AS rn,
 COUNT(*) OVER (PARTITION BY year) AS n
 FROM county_year WHERE balanced_panel=1
)
SELECT year, AVG(payment_to_income_ratio)*100 AS median_burden_pct
FROM ordered WHERE rn IN ((n+1)/2,(n+2)/2) GROUP BY year ORDER BY year;

-- 3. Largest point-estimate increases, not statistically significant ranks.
SELECT county_fips, county, state, burden_change_pp,
       price_contribution_pp, rate_contribution_pp, income_contribution_pp
FROM county_changes ORDER BY burden_change_pp DESC LIMIT 20;

-- 4. Lower-burden counties with above-median home-value appreciation.
WITH ranked AS (
 SELECT *, ROW_NUMBER() OVER (ORDER BY home_value_growth) AS rn,
 COUNT(*) OVER () AS n FROM county_changes
), cutoff AS (SELECT AVG(home_value_growth) AS g FROM ranked WHERE rn IN ((n+1)/2,(n+2)/2))
SELECT county, state, home_value_growth, payment_to_income_ratio
FROM county_changes, cutoff WHERE home_value_growth>g AND payment_to_income_ratio<0.20
ORDER BY home_value_growth DESC LIMIT 20;

-- 5. Compare 2025 payments with 2024 only where both years have 12 months.
SELECT a.county_fips,a.county,a.state,
       100*(b.monthly_payment/a.monthly_payment-1) AS payment_growth_pct
FROM county_year a JOIN county_year b ON a.county_fips=b.county_fips AND b.year=a.year+1
WHERE a.year=2024 AND a.housing_eligible=1 AND b.housing_eligible=1
ORDER BY payment_growth_pct DESC LIMIT 20;

-- 6. Audit the geographic mismatch instead of joining by county name.
SELECT county_fips,county,state,year FROM county_year
WHERE year<=2024 AND housing_eligible=1 AND income_eligible=0;
