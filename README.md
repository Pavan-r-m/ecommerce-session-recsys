
# Brazilian E-Commerce Analytics with dbt & DuckDB

This project analyzes the Olist Brazilian E-Commerce Public Dataset using dbt and DuckDB. It demonstrates modern analytics engineering best practices, from raw data ingestion to insightful business analysis.

## Project Goals
- Transform raw Olist CSVs into a clean analytics-ready data model
- Build reusable dbt models for orders, customers, products, payments, and more
- Generate actionable business insights (e.g., sales trends, customer behavior, product performance)
- Showcase modular, version-controlled analytics engineering

## Datasets
The following Olist datasets are included in the `seeds/` folder:
- orders.csv
- customers.csv
- order_items.csv
- products.csv
- payments.csv
- sellers.csv
- category_translation.csv

## How to Use
1. Install dependencies and activate your virtual environment
2. Run `dbt seed` to load the CSVs
3. Run `dbt run` to build models
4. Run `dbt test` to validate data
5. Explore insights in the `analyses/` folder

## Project Structure
- `models/` – dbt models (SQL transformations)
- `analyses/` – SQL analysis scripts
- `seeds/` – Raw CSV data
- `logs/` – dbt logs
- `macros/` – Custom dbt macros

---

### Using the starter project

Try running the following commands:
- dbt run
- dbt test


### Resources:
- Learn more about dbt [in the docs](https://docs.getdbt.com/docs/introduction)
- Check out [Discourse](https://discourse.getdbt.com/) for commonly asked questions and answers
- Join the [chat](https://community.getdbt.com/) on Slack for live discussions and support
- Find [dbt events](https://events.getdbt.com) near you
- Check out [the blog](https://blog.getdbt.com/) for the latest news on dbt's development and best practices
