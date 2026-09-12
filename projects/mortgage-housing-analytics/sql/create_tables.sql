-- Actual schema exported from the delivered database.
CREATE TABLE "county_year" (
"county_fips" TEXT,
  "county" TEXT,
  "state" TEXT,
  "year" INTEGER,
  "home_value" REAL,
  "months_available" INTEGER,
  "housing_eligible" INTEGER,
  "median_household_income" REAL,
  "income_lower" REAL,
  "income_upper" REAL,
  "census_county" TEXT,
  "census_state" TEXT,
  "avg_mortgage_rate" REAL,
  "rate_observations" INTEGER,
  "income_eligible" INTEGER,
  "eligible" INTEGER,
  "monthly_payment" REAL,
  "price_to_income_ratio" REAL,
  "payment_to_income_ratio" REAL,
  "burden_income_lower_bound" REAL,
  "burden_income_upper_bound" REAL,
  "home_value_yoy_growth" REAL,
  "income_yoy_growth" REAL,
  "balanced_panel" INTEGER
);
CREATE TABLE "county_changes" (
"county_fips" TEXT,
  "county" TEXT,
  "state" TEXT,
  "home_value" REAL,
  "median_household_income" REAL,
  "payment_to_income_ratio" REAL,
  "home_value_growth" REAL,
  "median_household_income_growth" REAL,
  "monthly_payment_growth" REAL,
  "burden_change_pp" REAL,
  "price_contribution_pp" REAL,
  "rate_contribution_pp" REAL,
  "income_contribution_pp" REAL
);
CREATE UNIQUE INDEX county_year_key ON county_year(county_fips,year);
CREATE INDEX county_year_state ON county_year(state,year);
