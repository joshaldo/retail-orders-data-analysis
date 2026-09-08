# Retail Orders Data Analyst Project

An end-to-end data analyst workflow built on a messy, intentionally flawed retail e-commerce dataset — covering data cleaning, SQL analysis, and visualization. Built as a first portfolio project ahead of Summer 2027 internship applications (bank analyst programs, fintech, and economics consulting roles).

## Project Overview

The dataset (`retail_orders_messy.csv`, 3,219 rows) simulates real-world messiness: inconsistent formatting, typos, missing values, duplicate rows, decimal-shift pricing errors, and corrupted email addresses. It moves through five phases — explore, clean, analyze, visualize, document — the way a stakeholder request would move through a real analytics team.

**Seven business questions anchor the analysis:**
1. Revenue trends over time
2. Category performance vs. discounting
3. Regional performance
4. Customer segmentation (repeat vs. one-time buyers)
5. Fulfillment and return rates
6. Payment method mix
7. Data quality summary

## Workflow

| Phase | Tool | What Happened |
|---|---|---|
| 1. Exploration | Excel | Initial look at the raw data to spot obvious issues before writing any code |
| 2. Cleaning | Python (pandas) | Cleaned all 16 columns, resolved data quality issues, added a derived flag column |
| 3. Analysis | MySQL / PopSQL | Loaded cleaned data into a MySQL database, wrote SQL for all 7 business questions |
| 4. Visualization | Python (matplotlib) | Built a revenue trend chart; remaining business questions visualized directly via SQL output |
| 5. Documentation | This README | Tied the workflow, decisions, findings, and problems together |

## Data Cleaning (Phase 2)

Cleaned with `pandas` in `clean_data.py`. The dataset went from 3,219 rows to 3,147 after removing 66 verified full-row duplicates — confirmed identical across every column before dropping, not just a repeated OrderID.

**Column-by-column summary:**

- **Quantity** — converted spelled-out numbers ("two", "five") to digits, took absolute value of negative entries, imputed remaining missing values with the median.
- **UnitPrice** — stripped `$` signs, corrected decimal-shift errors (values like $20,411 were actually $204.11), fixed negatives, imputed missing values using the median price within the same product category.
- **Discount** — standardized mixed formats (`"20%"` vs `0.2`) into a single decimal scale, filled missing values with 0 (assumed blank = no discount applied).
- **Region, Country, ProductCategory, PaymentMethod, OrderStatus, ProductName** — standardized whitespace and casing, then manually mapped known typos/variants (e.g. `"Est"` → `"East"`, `"Deliverd"` → `"Delivered"`).
- **CustomerName** — standardized casing, removed honorific prefixes (Mr., Mrs., Ms., Dr.) for consistency. *Known limitation:* surnames with "Mc"/"Mac" (e.g. "Mccann") were not corrected — a documented decision rather than something chased down individually, since fixing it would have needed a much more involved check for limited benefit.
- **OrderID** — standardized to a consistent `ORD-#####` format (998 rows were missing the prefix), then identified and removed true duplicate rows.
- **CustomerID** — checked for missing values and format consistency; no cleaning was needed, already fully valid.
- **Email** — 181 blank values left as `NaN`, since Email isn't used in any of the seven business questions. This was a deliberate distinction: a missing *key* field like OrderID would force exclusion, but a missing *informational* field doesn't need to cost you the row. 162 emails were corrupted with `.at.` in place of `@` (e.g. `angie.at.gmail.com`) — found and fixed using a simple check for the presence of an `@` symbol, rather than a full regex email validator, since the goal was to be able to explain the fix, not just apply it.
- **OrderDate / SignupDate** — parsed into proper datetime format. 86 OrderDate values couldn't be parsed and were left missing. Orders that occurred *before* the customer's signup date (a logical impossibility) were flagged in a new `order_before_signup` column rather than dropped, preserving the data for review. *Known limitation:* rows with an unparseable OrderDate default to `False` in this flag, since pandas treats `NaN` comparisons as `False` — this should be read as "unknown," not "confirmed after signup."

**Additional issue found during visualization (Phase 4):** 36 rows had `OrderDate` values from 2020–2022, isolated roughly two years before the dataset's real 2023–2024 range — most likely a typo'd year. These were excluded specifically from the revenue trend chart to avoid distorting it, while remaining in the dataset for other analyses. Finding this after Phase 2 was technically "complete" was a good reminder that data quality checks don't fully stop once cleaning is marked done — new issues can surface once you start actually using the data.

## Problems Encountered (and How They Were Solved)

Documenting these because working through them was as much a part of the learning process as the cleaning itself:

- **`LOAD DATA LOCAL INFILE` blocked by MySQL.** MySQL disables local file loading by default for security. Checking `SHOW VARIABLES LIKE 'secure_file_priv';` returned `NULL`, meaning server-side file loading was disabled entirely on this MySQL instance — not just restricted to a folder. Solved by loading the cleaned CSV through Python and SQLAlchemy instead of SQL's native file loader.
- **Python interpreter mismatch.** Installed packages (`sqlalchemy`, `mysql-connector-python`) were landing in an Anaconda Python environment, while Cursor was running scripts through a separate `/usr/local/bin/python3` installation — so the packages were "installed" but invisible to the script. Solved by explicitly installing with `/usr/local/bin/python3 -m pip install ...` to target the correct interpreter directly.
- **MySQL access denied.** The connection string initially assumed a root password that didn't exist locally. Solved by using an empty password (`root:@localhost`) to match how the local MySQL instance was actually configured.
- **`if_exists='append'` silently stacked duplicate data.** Rerunning the Python script multiple times kept appending another full copy of the dataset into the MySQL table instead of replacing it, inflating the row count to over 22,000. This was a good lesson in checking assumptions about default `pandas.to_sql()` behavior.
- **PopSQL returning 0 rows despite Python confirming a successful load.** Traced this by comparing `SELECT DATABASE();` results between sessions — PopSQL was silently defaulting into the built-in `mysql` system schema instead of the `retail_orders_project` database, meaning every "empty" result was querying the wrong database entirely, not the wrong table. Solved by explicitly running `USE retail_orders_project;` at the start of every PopSQL session going forward.

## SQL Analysis (Phase 3)

Data was loaded into a local MySQL database (`retail_orders_project`), ultimately via Python/SQLAlchemy after the native `LOAD DATA` approach was blocked (see Problems above). All 7 business questions were answered in SQL — see `analysis_queries.sql` for the full set of queries with comments explaining the logic.

## Visualizations (Phase 4)

One chart was hand-built in `matplotlib`, following the same revenue formula used in the SQL analysis:

- `revenue_over_time.png` — Monthly revenue trend, built step-by-step to fully understand the matplotlib workflow (grouping by month, plotting, labeling, and saving) rather than relying on generated code

The remaining business questions (category performance, regional performance, customer segmentation, order status, payment method, data quality) were answered directly in SQL — see `analysis_queries.sql` — with charting for those planned as a next step.

## Key Findings

- **Electronics** is the top revenue category, but also carries the deepest average discount — worth investigating whether that level of discounting is actually needed given its existing demand.
- Regional performance is fairly balanced ($137K–$163K across regions), with the **West** region leading.
- **90% of customers are repeat buyers** — a notably high retention rate. Worth validating against a larger or different time window before presenting as a headline metric, since a ratio this high is unusual for retail.
- The **return rate sits around 19%** of all orders, which stands out as high and would be worth flagging to a stakeholder for follow-up.
- Revenue fluctuates month-to-month in the $24K–$35K range across the dataset's real 2023–2024 window, without an obvious seasonal pattern.
- The dataset required real judgment calls at nearly every column — there was rarely a single "correct" cleaning approach, and documenting the reasoning mattered more than reaching a universally agreed-upon answer.

## Tools Used

- **Excel** — initial data exploration
- **Python** (pandas, matplotlib) — data cleaning and visualization
- **MySQL** (via PopSQL) — data storage and SQL analysis
- **SQLAlchemy** — Python-to-MySQL data loading

## Files in This Repository

- `retail_orders_messy.csv` — original raw dataset
- `retail_orders_cleaned.csv` — cleaned dataset (output of Phase 2)
- `clean_data.py` — full data cleaning, MySQL load, and revenue chart script
- `analysis_queries.sql` — SQL queries for all 7 business questions
- `revenue_over_time.png` — monthly revenue trend chart
- `README.md` — this file

## Skills Demonstrated

- Data cleaning and validation with Python (pandas)
- Handling missing data, duplicates, and inconsistent formatting
- Relational database design and SQL querying (MySQL)
- Data visualization with matplotlib
- Debugging and troubleshooting across a multi-tool pipeline
- Documenting assumptions and decisions for reproducibility

## Reflections

This was my first end-to-end data analyst project. Beyond the cleaning and analysis itself, it was a good exercise in diagnosing problems methodically — checking assumptions, isolating variables, and verifying results against a second source, rather than guessing at fixes. The database-connection issue in Phase 3, for example, ended up teaching me as much about how tools and environments interact as the actual data cleaning did. Going forward, I'd like to apply this same workflow to a project where the cleaning happens primarily in Excel, with Python and SQL used more purely for analysis.
