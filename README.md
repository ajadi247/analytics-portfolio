# Analytics Portfolio

An extensible analytics portfolio website, with a completed mortgage and housing affordability case study.

## Website

The public website is in `docs/`. GitHub Pages publishes this folder from the `main` branch. The homepage reads `docs/portfolio.json`, which holds profile information and project cards.

## Add another project

1. Add the completed project page and assets to `docs/`.
2. Add its title, category, period, description, tags, page URL, image, imageAlt, stat and statLabel to the `projects` array in `docs/portfolio.json`. The report field is optional.
3. Put its reproducible analysis under `projects/`.
4. Commit and push. GitHub Pages updates automatically.

Edit `name`, `title`, `bio`, `about`, and `links` in `docs/portfolio.json` to personalize the homepage. Link entries use `label` and `url`. All page and asset links are relative, so the site works at a GitHub Pages project URL.

## Mortgage & housing analysis

- [Project README](projects/mortgage-housing-analytics/README.md)
- [Full case study](projects/mortgage-housing-analytics/REPORT.md)
- [Analysis script](projects/mortgage-housing-analytics/analysis.py)
- [Notebook](projects/mortgage-housing-analytics/notebooks/housing_affordability_analysis.ipynb)
- [SQL queries](projects/mortgage-housing-analytics/sql/analysis_queries.sql)

The study combines the supplied Zillow snapshot, Census SAIPE annual income and Freddie Mac/FRED mortgage rates. Across 2,486 consistently observed counties, median modeled payment burden increased from 12.9% to 21.8% during 2015–2024. Read the case study for scope, uncertainty and costs excluded.


