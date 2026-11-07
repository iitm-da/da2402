import os, re
from build import build, load_outputs

HERE = os.path.dirname(os.path.abspath(__file__))
O = load_outputs(os.path.join(HERE, "out_endsem2.txt"))
SRC = open(os.path.join(HERE, "sol_endsem2.py"), encoding="utf-8").read()
B = {k: v.strip() for k, v in re.findall(r"# @@(\w+)\n(.*?)(?=\n# @@|\Z)", SRC, re.S)}

INTRO = r"""# Endsem practice paper 2

DA2402 · Data Curation and Visualization · Dr. Arun B Ayyar

Thirteen more problems across the whole course, in the order it was taught, on different data and
mostly different methods from paper 1: reshaping, validation regexes, HTML tables, robots.txt,
cursor pagination, Little's test, time-series gaps, skewed outliers, Isolation Forest and DBSCAN,
Fellegi-Sunter weights, SQL window functions, chained Dash callbacks, and Simpson's paradox.
Nothing here is marked. Each problem names a variable `q1` … `q13`. Put your result in it, run the
cell, then open **Answer** to check yourself. Most answers carry a short written part; try it in a
markdown cell of your own before reading ours.

Every dataset was generated for this paper with its defects planted. The files are the `p2_*` files
in [`endsem/practice/data/`](https://github.com/iitm-da/da2402/tree/master/endsem/practice/data),
written by `make_data2.py`.

**Setup.** Run the next cell first. `fetch(name)` downloads a file once into a local `data/` folder
and returns its path. In Colab, first run `!pip install dash`; the other libraries are already
there.
"""

def Q(tag, title, task, shape, written=None):
    d = dict(title=title, task=task, shape=shape, solution=B[tag], output=O[tag])
    if written:
        d["written"] = "**Written part.** " + written
    return d

QUESTIONS = [
    Q("q1", "pandas · wide to long, and a value in the wrong unit",
      """`p2_store_sales_wide.csv` has monthly sales in lakh for 8 stores, one column per month.

1. List the month columns pandas read as `object`, and say why.
2. Melt to long form (`store`, `month`, `sales_lakh`), convert `sales_lakh` with
   `pd.to_numeric(..., errors="coerce")` and count the missing values.
3. One cell was keyed in rupees. Find it as the value more than 100 times its store's median
   (use `groupby(...).transform("median")`) and convert it to lakh.
4. Compute each store's share of that month's total with `transform("sum")`, and each store's
   best month.""",
      "a dict with `object_columns`, `missing_after_coerce`, `fixed_cell` (store, month), "
      "`total_lakh`, `top_share_Dec` ([store, share]) and `best_month` (store → month).",
      """Porur opened in April and the export wrote `-` for January to March, so those three columns
became text, and `sum()` on them concatenates strings instead of failing. Without the unit fix,
OMR's July would read 1,262,000 lakh and every July share would be OMR's. `transform`
returns one value per row, aligned with the original index, which is what a per-row ratio needs;
`agg` returns one per group."""),

    Q("q2", "Regular expressions · validating KYC fields",
      """Each line of `p2_kyc.txt` is `Name | PAN: … | Mobile: … | Email: … | PIN: …`.

1. Pull the four fields out with one pattern using named groups.
2. Validate each field with `re.fullmatch`: PAN is 5 capital letters, 4 digits, 1 capital letter;
   a mobile is 10 digits starting 6-9; a PIN code is 6 digits not starting with 0; an email has a
   local part, `@`, a domain and a top-level domain of at least two letters.
3. Count the invalid values per field and the records valid on all four.""",
      "a dict with `records`, `invalid_per_field` (field → count) and `fully_valid`.",
      """`re.search` with the same patterns would pass a 9-character PAN inside a longer string or an
11-digit mobile, because search only needs the pattern somewhere in the value. `fullmatch` (or
`^…$` with `match`) requires the whole value to fit. The planted errors are a truncated PAN, a PAN
in lower case, a mobile starting with 5, a 9-digit mobile, `at` in place of `@`, a `.c` domain and
a PIN code starting with 0."""),

    Q("q3", "Scraping · an HTML results table",
      """`p2_results.html` has one table with a two-row header, constituency names with footnote
markers such as `[a]`, vote counts in Indian digit grouping (`5,01,499`), a dash where a party did
not contest, and a Total row written with Western grouping.

1. Read it with `pd.read_html(io.StringIO(html))` and flatten the header to
   `constituency, A, B, C, winner`.
2. Separate the Total row, strip the footnote markers, and convert the vote columns to numbers.
3. Check that your column sums equal the page's own Total row.""",
      "a dict with `seats`, `footnote_marks_left`, `not_contested` (list), `totals_match` (bool) "
      "and `seats_won` (party → seats).",
      """Leaving the Total row in doubles every column sum and adds a 13th "constituency". Removing
commas works for both digit groupings because the grouping is display only. The dash becomes NaN,
not 0: Party C got no votes in Arakkonam because it did not stand there. Checking your sums
against the page's Total is the cheapest test that the parse lost nothing."""),

    Q("q4", "Ethics · reading robots.txt with urllib",
      """`p2_robots.txt` is a shop's robots file. Parse it with `urllib.robotparser.RobotFileParser`
(`rp.parse(lines)`) and, as user agent `MyCrawler`, check these paths on `https://shop.example`:
`/products/kettle`, `/cart/checkout`, `/account/orders`, `/account/help/returns`,
`/products?sort=price`, `/accounts`. Also report the crawl delay, and whether `BadBot` may fetch
the home page.""",
      "a dict with `can_fetch` (path → bool), `crawl_delay` and `badbot_home`.",
      """Two of urllib's six answers disagree with the rules Google publishes (RFC 9309).
`/account/help/returns`: urllib applies the first rule that matches, `Disallow: /account`, and says
no; under RFC 9309 the longest match wins, so `Allow: /account/help` permits it. That error is on
the safe side. `/products?sort=price`: urllib does not understand `*` inside a path, so
`Disallow: /*?sort=` matches nothing and it says yes; the site meant no. That error is on the
unsafe side, and a crawler built on urllib would fetch pages the owner excluded. `/accounts` is
blocked by both readings, since `Disallow: /account` is a prefix and `/accounts` starts with it."""),

    Q("q5", "APIs · cursor pagination",
      """`p2_listings_1.json` is the first page of an API response. Each page has `results` and a
`next_cursor` naming the next file, `null` on the last page. Each result has a nested `price` and
`seller` and a list of `tags`.

1. Follow `next_cursor` until it is `None`, collecting every result.
2. Flatten with `pd.json_normalize`, count and drop records repeated across pages (by `id`).
3. Report median price per seller, the share of verified sellers, the number of listings with no
   tags, and the most common tag (`explode` the tag lists).""",
      "a dict with `pages`, `records_received`, `duplicates`, `unique`, `columns`, "
      "`median_price_by_seller`, `verified_share`, `no_tags`, `top_tag`.",
      """Record 5020 arrives on page 1 and again on page 2. Offset-paged APIs do this when a record is
inserted or re-sorted between requests, so deduplicating on the API's id is part of every paging
loop. `explode` turns an empty tag list into one row with NaN, so listings without tags survive
it and can be counted."""),

    Q("q6", "Missing values · Little's test, then the logistic",
      """`p2_staff.csv` has `age`, `tenure_yrs` (complete), `income_k` and `spend_k` (incomplete).

1. Implement Little's test as in the course notebook: means and covariance from the available data
   (`df.mean()`, `df.cov()`); for each missingness pattern add n × (pattern mean − overall mean)ᵀ
   Σ⁻¹ (pattern mean − overall mean) on its observed columns; degrees of freedom = total observed
   columns over all patterns − number of columns.
2. Little's test says whether some column breaks MCAR, not which. Fit a logistic regression of
   `income_k`'s missingness on `age` and `tenure_yrs` and report the LR p and the Wald p of each
   predictor.""",
      "a dict with `patterns`, `little_d2`, `df`, `little_p`, `income_LR_p` and `income_wald_p`.",
      """Little's test rejects MCAR for the file (d² = 28.64 on 8 df, p = 0.00037). The logistic finds
it in `income_k` (LR p = 4.5e-05), and the Wald tests put it on tenure (p = 0.00078) with age
clearing (p = 0.62), although age and tenure correlate at 0.73. Age's own relation to missingness
goes through tenure, and the Wald test asks what each predictor adds given the other. MAR on tenure
is what was planted; the data could not have ruled out MNAR on income."""),

    Q("q7", "Imputation · gaps in a time series",
      """`p2_sensor_hourly.csv` is a week of hourly temperatures with single dropped readings and one
12-hour outage. `p2_sensor_hourly_truth.csv` has the full series.

1. Label each run of consecutive missing values and its length (`miss.ne(miss.shift()).cumsum()`
   gives a run id).
2. Fill four ways: series mean, forward fill, linear interpolation, and the same hour the day
   before (`shift(24)`).
3. Report RMSE against the truth separately on single gaps and on the outage.""",
      "a DataFrame with one row per method and columns `rmse_single_gaps`, `rmse_12h_outage`.",
      """Linear interpolation wins on single gaps (0.15), because the readings either side of one hour
pin it down. Across the 12-hour outage it draws a straight line through a daily cycle, and the
same hour yesterday does better (0.51 against 0.68) because it carries the cycle. Forward fill is
worst on the outage (4.43): it holds the last reading flat for half a day. The mean ignores time
altogether. The choice depends on gap length, so measure gap lengths before choosing a method."""),

    Q("q8", "Outliers · rules on a skewed column",
      """`p2_incomes.csv` has 500 household incomes in lakh per year: right-skewed, with five planted
errors: two values 1,000 times too small, two 100 times too large, and one junk value.
`p2_incomes_truth.csv` marks them.

Apply the IQR rule (1.5) and the modified z-score (3.5) to the raw column and to `log10` of it.
For each of the four, count flags, planted errors caught and clean values flagged.""",
      "a DataFrame with one row per rule and columns `flagged`, `planted_caught`, `clean_flagged`.",
      """On the raw scale both rules assume a roughly symmetric middle and flag the long right tail of
honest high earners (17 and 9 clean flags) while missing the two tiny values, which sit inside the
lower fence. On the log scale incomes are close to symmetric, the unit slips sit orders of magnitude
away on both sides, and the modified z catches all five with no clean flag. Transforming first is an
assumption about the shape of the clean data, so check that shape with a histogram before
trusting it."""),

    Q("q9", "Outliers · Isolation Forest and DBSCAN",
      """`p2_transactions.csv` has card transactions (`hour`, `amount`); `p2_transactions_truth.csv`
marks 12 planted frauds: 9 large night-time payments and 3 night-time payments of ordinary size.

1. Build features `hour` and `log10(amount)`, standardised.
2. Fit `IsolationForest(n_estimators=200, contamination=0.02, random_state=42)`; flagged = predict
   returns −1.
3. Fit `DBSCAN(eps=0.5, min_samples=8)`; flagged = label −1 (noise).
4. Score precision and recall for each.""",
      "a DataFrame with rows `isolation forest`, `DBSCAN noise` and columns `flagged`, `true_pos`, "
      "`precision`, `recall`.",
      """Isolation Forest misses one of the ordinary-sized night payments (3:26 am, ₹505), which is
isolated only in `hour`, and `contamination=0.02` fixes the flag count at 2% of rows whatever the
data holds. DBSCAN catches all 12 but calls 8 honest transactions noise, early-morning and late-night
payments and the smallest and largest daytime amounts, where the density thins. Both depend on a setting the data
cannot choose: the contamination rate, or eps and min_samples."""),

    Q("q10", "Duplicates · Fellegi-Sunter weights",
      """`p2_pairs.csv` has 400 candidate record pairs, each with 0/1 agreement on `surname`, `dob`,
`pincode` and `phone`. Use these m and u probabilities:

| field | m | u |
|---|---|---|
| surname | 0.95 | 0.05 |
| dob | 0.90 | 0.003 |
| pincode | 0.85 | 0.10 |
| phone | 0.80 | 0.001 |

1. Agreement weight log₂(m/u), disagreement weight log₂((1−m)/(1−u)), per field.
2. Score each pair as the sum of its four weights.
3. With `p2_pairs_truth.csv`, report flagged pairs, precision and recall at thresholds of 0, 5,
   10 and 14 bits.""",
      "a tuple `(weights, table)`: weights per field (agree, disagree) and the threshold table.",
      """Agreeing on phone is worth 9.6 bits and on surname 4.2, because a shared surname is far more
common by chance (u = 0.05). Two groups decide the thresholds. Eight true matches moved and changed
phone; they agree on surname and dob only and score 7.57, so a threshold of 10 loses them. Twelve
family pairs share surname, pincode and phone and score 13.66, above 10. The model treats fields as
independent given match status; in a family they agree together, so the score overstates the
evidence. Only the 14-bit threshold removes them, at a recall of 0.617. A first-name field would
separate them."""),

    Q("q11", "Storage · normalising into SQLite, then a window function",
      """`p2_order_lines.csv` repeats each product's name, category and price on every line.

1. Split it into `products` (one row per product) and `order_lines` (line_id, order_date,
   product_id, qty). Create both tables in an in-memory SQLite database with primary keys and a
   foreign key, and load them.
2. How many cells does the split save?
3. SQL: months (`strftime('%Y-%m', order_date)`) with revenue over 1.5 lakh, using `HAVING`.
4. SQL: the top product by revenue in each category with `ROW_NUMBER() OVER (PARTITION BY …)`.""",
      "a dict with `cells_saved`, `months_over_1.5_lakh` (list) and `top_per_category` "
      "(category → product).",
      """`WHERE` filters rows before grouping and cannot see `SUM(...)`; `HAVING` filters the groups.
The window function ranks within each category without collapsing rows, which a `GROUP BY
category` with `MAX` cannot do, since `MAX` returns the revenue and not the product that earned it.
Normalising also means a price change is one update in `products` instead of hundreds of lines
that can disagree."""),

    Q("q12", "Dash · chained callbacks, State and PreventUpdate",
      """With Gapminder (`px.data.gapminder()`):

1. A continent dropdown (`cont`) fills the options and first value of a country dropdown
   (`country`).
2. A button (`go`) shows the life expectancy for the chosen country and a year typed in an input
   (`year`). The country and year are `State`, so typing does not fire the callback; only the
   click does.
3. Raise `PreventUpdate` before the first click. If the year has no row, say so instead of
   failing.

Test both callbacks as plain functions: `countries("Oceania")`, then `show(None, "India", 2007)`
(should raise), `show(1, "India", 2007)` and `show(1, "India", 2005)`.""",
      "a tuple `(options, first_value, prevent_raised, text_2007, text_2005)`.",
      """With `Input` on the year, every keystroke would fire the callback and look up years like 2, 20
and 200. `State` passes the current value only when the button fires. Gapminder has rows every five
years, so 2005 does not exist; a callback that indexes `.item()` on an empty selection raises an
error inside the app, which is why the empty case is handled first."""),

    Q("q13", "Honest charts · Simpson's paradox",
      """`p2_recovery.csv` has made-up patients and recoveries by hospital and severity.

1. Recovery rate per hospital overall.
2. Recovery rate per hospital within each severity.
3. Standardise: weight each hospital's severity-specific rates by the pooled severity mix of all
   2,000 patients.
4. A bubble chart scaled the bubble **radius** by value. How many times larger does a bubble for
   twice the value look, in area?""",
      "a dict with `overall`, `by_severity`, `standardised` and `area_ratio_if_radius_scaled_for_2x`.",
      """Town Clinic looks better overall (88.8% against 85.0%) and City Hospital is better at both
severities (95% vs 92% mild, 70% vs 60% severe). City takes 400 severe cases out of 1,000; Town
takes 100. Standardised to one case mix, City leads 88.8% to 84.0%. A chart of overall rates
answers "where did more patients recover"; small multiples or grouped bars by severity answer
"which hospital treats better". Scaling a bubble's radius draws a 2× value at 4× the area, and
readers judge area, so area should be proportional to the value. `px.scatter(size=...)` does
this (it sets `sizemode="area"`); in `graph_objects` the default sizemode is `"diameter"`."""),
]

SPEC = {
    "colab_path": "endsem/practice/endsem_practice_2.ipynb",
    "intro": INTRO,
    "setup": B["setup"],
    "questions": QUESTIONS,
    "closing": "That is paper 2. Errors you spot in it: tell Dr. Ayyar in class or on Moodle.",
}

if __name__ == "__main__":
    out = os.path.join(HERE, "..", "..", "endsem", "practice", "endsem_practice_2.ipynb")
    build(SPEC, os.path.normpath(out))
