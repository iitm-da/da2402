import os, re
from build import build, load_outputs

HERE = os.path.dirname(os.path.abspath(__file__))
O = load_outputs(os.path.join(HERE, "out_endsem.txt"))
SRC = open(os.path.join(HERE, "sol_endsem.py"), encoding="utf-8").read()
B = {k: v.strip() for k, v in re.findall(r"# @@(\w+)\n(.*?)(?=\n# @@|\Z)", SRC, re.S)}

INTRO = """# Endsem practice paper

DA2402 · Data Curation and Visualization · Dr. Arun B Ayyar

Thirteen problems across the whole course, in the order it was taught: pandas, regular expressions,
scraping, JSON, missing values, imputation, outliers, duplicates, storage, Dash and honest charts.
Nothing here is marked. Each problem names a variable `q1` … `q13`. Put your result in it, run the
cell, then open **Answer** to check yourself. Most answers also carry a short written part; try it
in a markdown cell of your own before reading ours.

Every dataset was generated for this paper with its defects planted, so each answer can be checked
against what was actually planted. The data files sit in
[`endsem/practice/data/`](https://github.com/iitm-da/da2402/tree/master/endsem/practice/data), with
`make_data.py`, which wrote them.

**Setup.** Run the next cell first. `fetch(name)` downloads a file once into a local `data/` folder
and returns its path, so every later cell reads from disk. In Colab, first run
`!pip install dash dash-bootstrap-components rapidfuzz`; the other libraries are already there.
"""

def Q(tag, title, task, shape, written=None, stub=None):
    d = dict(title=title, task=task, shape=shape, solution=B[tag], output=O[tag])
    if written:
        d["written"] = "**Written part.** " + written
    if stub:
        d["stub"] = stub
    return d

QUESTIONS = [
    Q("q1", "pandas · a merge that changes the row count",
      """`orders.csv` holds 1,200 orders and `customers.csv` maps `customer_id` to `city`.

1. Inner-merge the two on `customer_id` and compare the row count with `len(orders)`.
2. Find the `customer_id` that appears twice in `customers`, and count the orders whose
   `customer_id` is missing from `customers` (the orphan orders) and their total `amount`.
3. Fix the merge: keep the **last** row for the duplicated customer (they moved city), use a left
   merge with `validate="many_to_one"`, and fill the orphans' city with `"Unknown"`.
4. Pivot revenue by `city` (rows) and quarter of `order_date` (columns). Report the city with the
   highest total and its Q4 revenue.""",
      "a dict with keys `orders`, `inner_merge_rows`, `duplicated_customer`, `orphan_orders`, "
      "`orphan_revenue`, `top_city`, `top_city_Q4`.",
      """The inner merge returned 1,202 rows, more than the 1,200 orders. Two things happened at once:
the 9 orphan orders were dropped, and customer 42's 11 orders were each matched to both of their
city rows, adding 11. The count went up by 2, which hides both defects. `validate="many_to_one"`
raises an error on the duplicated key instead, and that is why it belongs on every lookup merge."""),

    Q("q2", "Regular expressions · delivery messages",
      """`messages.txt` mixes delivery confirmations with OTPs, cancellations, a promotion and a
survey request. The confirmations come in three layouts, the currency is written `Rs.`, `Rs`,
`INR` or `₹`, amounts may carry thousands commas, and dates are `dd/mm/yyyy` or `dd-Mon-yyyy`.

1. Keep only lines that mention a delivery **and** carry an order id `#` + one capital letter +
   four digits.
2. From each, extract `order_id`, `date`, `amount` (a float) and the six-digit `pincode`.
3. Parse the dates with `pd.to_datetime(..., format="mixed", dayfirst=True)`.""",
      "a dict with `deliveries` (row count), `total_amount`, `by_month` "
      "(deliveries per month name, as a dict) and `top_city_prefix` (the most common first three "
      "digits of the pincode).",
      """"Rate your delivery on 12/10/2026 and win Rs. 500" mentions a delivery and has a date, so a
filter on the word alone keeps it; it has no order id, which is what removes it. The OTP lines have
a six-digit number that the pincode pattern would happily match, which is why the line filter
comes before extraction. The amount pattern needs the comma inside the character class: 20 of the 60
amounts are written like `Rs. 1,870.23`, and `\\d+\\.\\d{2}` does not match them at all."""),

    Q("q3", "Scraping · pagination and a sponsored duplicate",
      """`shop_p1.html` is page 1 of a product listing. Each product is a `div.card` with a `data-id`,
an `h3.title`, a `span.price` such as `₹1,299` and a `span.rating` such as `4.2 ★`. Out-of-stock
cards have no price span at all. Each page links to the next with `a.next`; the last page has none.

1. Start at page 1 and follow `a.next` until it runs out. Do not hard-code the page count.
2. Parse every card into a row with `id`, `title`, `price` (NaN when out of stock), `rating` and
   whether the card's class list contains `sponsored`.
3. Drop duplicates on `id`, keeping the first sighting.""",
      "a tuple `(cards_seen, unique_products, out_of_stock, mean_price)`, mean rounded to 2 dp.",
      """Pages 2 and 3 each open or close with a sponsored card that repeats a product listed
earlier, so 34 cards describe 32 products. Deduplicating on the title would be wrong here: the
`data-id` is the site's own key, and two products can share a title. A loop on `a.next` keeps
working when the shop adds a fourth page; `range(1, 4)` silently stops at three."""),

    Q("q4", "APIs · flattening nested JSON",
      """`weather.json` is a saved API response: a list of `stations`, each with an `id`, a `name`, a
nested `location` and a list of `readings`. Some readings have no `rain_mm` key.

1. Flatten it with `pd.json_normalize`, one row per reading, carrying the station's `id`, `name`
   and `location.lat` as metadata.
2. Per station name, report the number of readings, mean `temp_c`, number of readings with no
   rain value, and total rain.""",
      "a DataFrame indexed by station name with columns `readings`, `mean_temp`, `rain_missing`, "
      "`rain_total`, rounded to 2 dp.",
      """`rain_total` is not comparable across stations. Ennore sent 5 readings because the station went
offline, and `sum()` skips the 3 missing rain values at Tambaram as though no rain fell. A missing
key in an API response is a missing value; it is zero rain only if the API documents it that way."""),

    Q("q5", "Missing values · testing MCAR",
      """`clinic.csv` has 500 patients. `age`, `bmi` and `sbp` are complete; `cholesterol` and
`sleep_hours` have missing values. For each of the two incomplete columns:

1. Run the permutation test on `age`: the statistic is |mean age of rows with the value missing −
   mean age of the rest|, 5,000 shuffles of the missingness indicator, one
   `np.random.default_rng(0)` per column, p = (1 + count of shuffled statistics ≥ observed) / (1 + 5000).
2. Fit a logistic regression of the missingness indicator on `age`, `bmi`, `sbp` with statsmodels
   and report the likelihood-ratio χ² and its p-value (`llr`, `llr_pvalue`).""",
      "a DataFrame with rows `cholesterol`, `sleep_hours` and columns `missing`, `perm_diff_age`, "
      "`perm_p`, `LR_chi2`, `LR_p`.",
      """Which column rejects MCAR, and what does the rejection leave open?

`cholesterol` rejects MCAR on both tests: patients missing it are 12.9 years older on average
(p = 0.0002), and the logistic's LR p is 5.5e-16. `sleep_hours` clears both (p = 0.40, 0.64). Both
tests share one null, MCAR. Rejecting it leaves MAR and MNAR standing together; no test separates
them, because MNAR depends on the value that was never recorded. Clearing it shows only that
missingness is unrelated to the columns tested."""),

    Q("q6", "Imputation · scored against the truth",
      """`clinic_truth.csv` holds `cholesterol` before any value was deleted. Fill the missing
`cholesterol` values three ways:

1. **mean** of the observed values;
2. **regression** on `age` and `bmi`, fitted on the complete rows;
3. **KNN** with `KNNImputer(n_neighbors=5)` on `age`, `bmi`, `sbp`, `cholesterol`, standardised
   first (subtract the mean, divide by the sd) and transformed back.

For the truth and each filled column, report RMSE on the filled rows only, mean, sd and correlation
with `age`.""",
      "a DataFrame with rows `truth`, `mean`, `regression`, `knn` and columns `rmse_filled`, "
      "`mean`, `sd`, `corr_age`, rounded to 3 dp.",
      """Which fill would you use, and what is still wrong with it?

Regression has the lowest RMSE (21.2 against 35.8 for the mean). The mean fill shrinks the sd from
32.6 to 27.0 and drags the correlation with age from 0.682 to 0.546, and its mean is 5.5 low:
cholesterol is MAR on age, so the observed values come from younger patients. Regression puts every
filled point on the fitted line, so the correlation overshoots to 0.724 and the sd is still short
(30.1). Any model that fills with its prediction removes the scatter around it."""),

    Q("q7", "Outliers · three univariate rules",
      """`delivery_times.csv` has 300 delivery times in minutes, including a batch of orders that
stalled at the hub. Flag outliers in `minutes` three ways:

1. z-score, |z| > 3 (sample mean and sd);
2. IQR rule, outside [Q1 − 1.5·IQR, Q3 + 1.5·IQR];
3. modified z-score, 0.6745·(x − median)/MAD, |value| > 3.5.

Also list the values above the median that the IQR rule flags and the z-score misses.""",
      "a dict with the flag count per rule, `mean, sd` and the list of values z misses.",
      """Why does the z-score miss values the other two catch?

Masking. The 18 stalled orders pull the mean up to 37.1 and the sd up to 23.2 (the normal batch
has a sd near 6), so a 90-minute delivery sits under 3 sds from the mean. The median and IQR barely
move when 6% of the data is extreme, so the other two rules see it. The IQR rule's extra flags
include 54.0 at the slow end and 14.7 at the fast end, ordinary orders from the normal batch: a
flag says a value is unusual, and deciding whether it is wrong takes knowing how it was produced."""),

    Q("q8", "Outliers · Mahalanobis against LOF",
      """`sensors.csv` has temperature and vibration readings from two machines that run at
different settings, with three planted outliers among them.

1. Compute each reading's squared Mahalanobis distance from the overall mean using the overall
   covariance, and flag readings above `stats.chi2.ppf(0.975, df=2)`.
2. Standardise the two columns and fit `LocalOutlierFactor(n_neighbors=20)`. Take the 5 readings
   with the lowest `negative_outlier_factor_`.""",
      "a dict with `mahalanobis` (sorted reading ids flagged) and `lof_top5` (ids, most outlying first).",
      """The planted readings are 143 (just off machine A's tight cloud), 113 (between the machines)
and 240 (far from both). Why does Mahalanobis miss 143 and 113?

One mean and one covariance describe a single elliptical cloud. With two machines, the overall mean
falls in the empty space between them: reading 113 sits almost on it (d² = 0.01). Machine B's
spread inflates the covariance, so 143 at d² = 0.41 looks ordinary, while normal points at B's edge
get flagged instead. LOF compares each point with its own neighbours, so 143 has the largest
factor of all. 113 escapes LOF too (rank 12): with only a few points nearby, it reads as sparse
rather than isolated. Neither method knows which machine a reading came from; fitting one per
machine is the fix when that label exists."""),

    Q("q9", "Duplicates · normalise, block, match",
      """`members.csv` has sign-ups from one club, with people who registered more than once. Their
names vary in case, spacing, a `Dr.` prefix, a one-letter typo or a `Surname, First` order; their
phone numbers vary as `9840012345`, `+91 98400 12345`, `+91-9840012345` or `09840012345`. A few
signed up again with a new number. `members_truth.csv` maps each `record_id` to a `person_id`.

1. Clean names (lower case, collapse spaces, drop `dr.`, put `surname, first` back in order) and
   reduce each phone to its last 10 digits.
2. Block on `city`: form candidate pairs only within a city, each pair once.
3. Score name similarity with `rapidfuzz.distance.JaroWinkler.similarity`.
4. For each rule, count predicted pairs, true positives, precision and recall: raw phone equal;
   clean phone equal; name JW ≥ 0.93; clean phone equal **or** name JW ≥ 0.97.""",
      "a tuple `(all_pairs, pairs_after_blocking, true_pairs, table)` with the rules as rows.",
      """Blocking on city cuts 30,135 pairs to 7,474 and loses no true pair, since a person's copies
share a city here. Comparing raw phones finds 5 of 105 true pairs; cleaning them finds 92, with no
false match, and misses the people with a new number. Names alone find all 105 but bring 20 false
pairs: 5 are different people with exactly the same name, and most of the rest share a first name,
which Jaro-Winkler rewards because it weights the common prefix (`karthik raman` against
`karthik nair` scores 0.934). The combined rule trades a little of each:
precision 0.945, recall 0.990. Every threshold here was chosen with the truth file open; on real
data you would label a sample of pairs to choose it."""),

    Q("q10", "Storage · what a CSV forgets",
      """`meters.csv` and `meters.parquet` hold the same 400 meter readings. Read both with pandas
defaults and compare the dtypes. Add a row showing the first `meter_id` from each file as a
string.""",
      "a DataFrame with columns `csv`, `parquet`, one row per column plus the `first meter_id` row.",
      """CSV stores text and no types, so pandas guesses: `meter_id` `020770` becomes the integer
20770, the date stays a string and the zone becomes object. Parquet stores the schema with the data,
so the leading zero, the datetime and the category come back as written. To read the CSV
correctly, say so: `pd.read_csv(..., dtype={"meter_id": str}, parse_dates=["read_on"])`."""),

    Q("q11", "Storage · SQLite joins and anti-joins",
      """`shop.db` has tables `customers` (customer_id, name, city), `products` (product_id,
product, category, price) and `orders` (order_id, customer_id, product_id, qty, order_date).
Write SQL and run it with `pd.read_sql`:

1. Revenue (`qty × price`) and order count per city, highest revenue first.
2. Customers who never ordered, with a `LEFT JOIN … WHERE o.order_id IS NULL`.
3. Products never sold, with `NOT EXISTS`.""",
      "a dict with `top_city`, `top_revenue` (int), `never_ordered` (list of ids) and `unsold` "
      "(list of product names).",
      """An inner join of customers to orders drops the 5 customers who never ordered without any
warning, which is why the anti-join needs the LEFT JOIN and the `IS NULL` test on a column from
the right-hand table."""),

    Q("q12", "Dash · a callback you can test without a browser",
      """Use Gapminder (`px.data.gapminder()`, bundled with plotly).

1. Lay the app out with `dash_bootstrap_components`: a row with a 4-wide column holding a
   continent `dcc.Dropdown` (id `continent`, default `"Asia"`) and an `html.H4` (id `kpi`) under
   it, and an 8-wide column holding a `dcc.Graph` (id `trend`).
2. Write one callback from `continent` to both outputs: the KPI text
   `"<continent>: median life expectancy <x.x> years in 2007"` and a line chart of median
   `lifeExp` per year.
3. A decorated callback is still a plain Python function. Call it with `"Africa"` and inspect what
   it returns. Run `app.run(jupyter_mode="inline")` only to look at the app.""",
      "a tuple `(kpi_text, first three y values rounded to 1 dp, number of x points)` from "
      "`update(\"Africa\")`.",
      """Which gestalt principle tells a reader that the dropdown controls the KPI and not just the
chart? Proximity and common region: the dropdown and the KPI share one column, so they read as a
group, and the chart sits in its own. Moving the KPI into the chart's column would make it read as
the chart's title. Testing the callback as a function catches a wrong median or a wrong label
without starting a server."""),

    Q("q13", "Honest charts · lie factor and per capita",
      """`enrolment.csv` has made-up college enrolment and population figures, in lakh, for five
states in 2024 and 2025.

1. A news graphic drew Tamil Nadu's 2024 and 2025 enrolment as bars on an axis starting at 10.0.
   Compute the change the bars show (the change in bar height above 10.0), the actual change, and
   the lie factor (shown ÷ actual).
2. For 2025, compute enrolment per 1,000 people and draw an honest horizontal bar chart sorted by
   it, axis from zero (plotly's default for bars).
3. Report which state leads by raw count and which leads per 1,000.""",
      "a dict with `shown_change_%`, `actual_change_%`, `lie_factor`, `top_by_count`, "
      "`top_per_1000` and `per_1000` (state → value).",
      """A 4.0% rise is drawn as a 195% rise, a lie factor of 48.6. Tamil Nadu leads on raw count only
because it is the most populous of the five; per 1,000 people, Goa leads at 21.2. Goa's 0.34 lakh
is the smallest count in the table, so its rate moves most from one year's noise, and a
choropleth of the raw counts would paint Tamil Nadu darkest and say nothing about enrolment. For a
per-1,000 map, use a sequential scale: one hue from light to dark, since the quantity runs one way
from low to high."""),
]

STUB = {"q12": "# build app, write update(continent), then:\nq12 = ...   # your answer\nq12"}
for i, q in enumerate(QUESTIONS, 1):
    if f"q{i}" in STUB:
        q["stub"] = STUB[f"q{i}"]

SPEC = {
    "colab_path": "endsem/practice/endsem_practice.ipynb",
    "intro": INTRO,
    "setup": B["setup"],
    "questions": QUESTIONS,
    "closing": "That is the paper. Errors you spot in it: tell Dr. Ayyar in class or on Moodle.",
}

if __name__ == "__main__":
    out = os.path.join(HERE, "..", "..", "endsem", "practice", "endsem_practice.ipynb")
    build(SPEC, os.path.normpath(out))
