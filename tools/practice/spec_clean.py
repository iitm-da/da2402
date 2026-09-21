from build import build, load_outputs
O = load_outputs("out_clean.txt")

INTRO = """# Practice · data cleaning

DA2402 · Data Curation and Visualization · Dr. Arun B Ayyar

Nine questions covering Lectures 1 to 3: the missingness patterns, the three tests for the mechanism,
and the imputation scoreboard. Each question names a variable. Put your
result in that variable and run the cell. The worked answer sits under **Answer**. Click it open
once you have tried.

**The data.** `panel.csv`, 500 households, written for this worksheet the way `survey.csv` was
written for the lectures: the mechanism is known because it was planted.

| column | mechanism | missing |
|---|---|---|
| `power_backup` | MCAR, a flat tablet-failure rate | 22 |
| `rent` | MAR on `age` and `household_size` | 154 |
| `savings` | MNAR on itself, low savers withhold | 74 |

`age`, `household_size`, `education_years` and `commute_min` are complete.

`truth_rent` holds the rent values before any were deleted. No real study has that, which is why
the last question can be scored at all.
"""

SETUP = """import io
import requests
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from sklearn.impute import KNNImputer

URL = "https://raw.githubusercontent.com/iitm-da/da2402/master/data%20cleaning/practice/data/"
panel = pd.read_csv(URL + "panel.csv")

def load_npy(name):
    return np.load(io.BytesIO(requests.get(URL + name).content))

truth_rent = load_npy("truth_rent.npy")

NUM = ["age", "household_size", "education_years", "commute_min", "rent", "savings"]
print(panel.isna().sum().to_string())"""

GIVEN_MD = """### Given: the ML mean and covariance under missingness

Little's test needs μ̂ and Σ̂ estimated from all 500 rows, which is the EM step from Lecture 2. It is
supplied here so Q5 is the assembly of the statistic rather than the estimator. Q1 to Q4 do not
need it."""

GIVEN = '''def em_mean_cov(X, iters=300, tol=1e-8):
    """ML mean and covariance of X (n by p, holding NaN), by EM."""
    X = np.asarray(X, float)
    n, p = X.shape
    mu = np.nanmean(X, 0)
    S = np.cov(np.where(np.isnan(X), mu, X), rowvar=False)
    for _ in range(iters):
        T1 = np.zeros(p)
        T2 = np.zeros((p, p))
        for i in range(n):
            row = X[i]
            obs = ~np.isnan(row)
            mis = ~obs
            z = row.copy()
            C = np.zeros((p, p))
            if mis.any():
                B = S[np.ix_(mis, obs)] @ np.linalg.pinv(S[np.ix_(obs, obs)])
                z[mis] = mu[mis] + B @ (row[obs] - mu[obs])
                C[np.ix_(mis, mis)] = S[np.ix_(mis, mis)] - B @ S[np.ix_(obs, mis)]
            T1 += z
            T2 += np.outer(z, z) + C
        mu_new, S_new = T1 / n, T2 / n - np.outer(T1 / n, T1 / n)
        done = max(np.abs(mu_new - mu).max(), np.abs(S_new - S).max()) < tol
        mu, S = mu_new, S_new
        if done:
            break
    return mu, S'''

Q = [
 dict(title="Missingness patterns", out="q1",
      task="Count the rows of each missingness pattern over `rent`, `savings` and `power_backup`.\nSeven of the eight possible patterns occur.",
      shape="a Series indexed by the three booleans.",
      solution='q1 = panel[["rent", "savings", "power_backup"]].isna().value_counts()\nq1'),
 dict(title="Group-mean comparison on rent", out="q2",
      task="Test 1 from Lecture 2. Split `age` by whether `rent` is missing and run Welch's t-test\nacross the two groups. Report the statistic and the p-value.",
      shape="a tuple `(t, p)`.",
      solution='R = panel["rent"].isna()\nt, p = stats.ttest_ind(panel["age"][R], panel["age"][~R], equal_var=False)\n\nq2 = (round(float(t), 3), float(f"{p:.3g}"))\nq2'),
 dict(title="The permutation version, on power_backup", out="q3",
      task="The same comparison for `power_backup`, with the null built by relabelling instead of\nlooked up in a t distribution. 5,000 permutations, `np.random.default_rng(0)`, the statistic being\nthe difference in mean `age` between the two groups. Report the observed difference in years and\nthe two-sided p. A loop that draws differently will move the last digit.",
      shape="a tuple `(observed_difference, p)`.",
      solution='''rng = np.random.default_rng(0)
age = panel["age"].to_numpy()
B = panel["power_backup"].isna()
obs = age[B].mean() - age[~B].mean()

null = np.empty(5000)
for i in range(5000):
    idx = rng.permutation(len(panel))
    null[i] = age[idx[:B.sum()]].mean() - age[idx[B.sum():]].mean()

q3 = (round(float(obs), 3), round(float((np.abs(null) >= abs(obs)).mean()), 4))
q3'''),
 dict(title="Degrees of freedom for Little's test", out="q4",
      task="Over the six columns in `NUM`, count the missingness patterns, the observed-column slots\nthey contribute between them, and the degrees of freedom `sum(|J_k|) - p`.",
      shape="a tuple `(patterns, slots, df)`.",
      solution='patt = panel[NUM].notna().apply(tuple, axis=1)\n\nslots = sum(sum(k) for k in patt.unique())\nq4 = (len(patt.unique()), slots, slots - len(NUM))\nq4'),
 dict(title="Little's test on the six numeric columns", out="q5",
      task="Assemble `d2 = sum_k n_k (xbar_k - mu_Jk)' inv(Sigma_Jk) (xbar_k - mu_Jk)`, taking μ̂ and Σ̂\nfrom `em_mean_cov` on all 500 rows and cutting each down to the columns its pattern observes.\nReport the statistic, its degrees of freedom and the p-value.",
      shape="a tuple `(d2, df, p)`.",
      solution='''def littles_test(df, cols):
    X = df[cols].to_numpy(float)
    mu, S = em_mean_cov(X)

    groups = {}
    for i, row in enumerate(~np.isnan(X)):
        groups.setdefault(tuple(row), []).append(i)

    d2, dfree = 0.0, 0
    for key, idx in groups.items():
        J = np.array(key, bool)
        if not J.any():
            continue
        diff = X[np.ix_(idx, np.where(J)[0])].mean(0) - mu[J]
        d2 += len(idx) * diff @ np.linalg.pinv(S[np.ix_(J, J)]) @ diff
        dfree += J.sum()
    dfree -= len(cols)
    return d2, int(dfree), float(stats.chi2.sf(d2, dfree))


d2, dfree, pval = littles_test(panel, NUM)
q5 = (round(float(d2), 2), dfree, float(f"{pval:.3g}"))
q5'''),
 dict(title="Logistic on the rent missingness indicator", out="q6",
      task="Test 3. Fit `rent.isna() ~ age + household_size + education_years` with `sm.Logit` and\nreport the model-level likelihood-ratio test: `2 * (llf - llnull)`, its degrees of freedom and its\np-value.",
      shape="a tuple `(lr_chi2, df, p)`.",
      solution='''PRED = ["age", "household_size", "education_years"]

def fit_logit(col):
    y = panel[col].isna().astype(int)
    return sm.Logit(y, sm.add_constant(panel[PRED])).fit(disp=0)


m = fit_logit("rent")
q6 = (round(float(2 * (m.llf - m.llnull)), 2), int(m.df_model),
      float(f"{m.llr_pvalue:.3g}"))
q6'''),
 dict(title="Wald table for that fit", out="q7",
      task="Report coefficient, standard error, odds ratio and Wald p for every term of the same fit,\nintercept included. The odds ratio is `exp(coef)`, the multiplier on the odds of withholding per\nunit of the predictor.",
      shape="a DataFrame, 4 rows by 4 columns.",
      solution='q7 = pd.DataFrame({"coef": m.params.round(4), "se": m.bse.round(4),\n                   "OR": np.exp(m.params).round(3),\n                   "p": m.pvalues.map(lambda v: float(f"{v:.3g}"))})\nq7'),
 dict(title="The same test on all three incomplete columns", out="q8",
      task="Fit that model for `rent`, `savings` and `power_backup`, and report the LR p-value for each.\nTwo of the three reject. `savings` is missing on its own value, and the test rejects for it too, so\na rejection here does not separate MAR from MNAR.",
      shape="a Series indexed by column.",
      solution='q8 = pd.Series({c: float(f"{fit_logit(c).llr_pvalue:.3g}")\n                for c in ["rent", "savings", "power_backup"]}, name="LR p")\nq8'),
 dict(title="Imputation scored against the truth", out="q9",
      task="Fill `rent` four ways: the column mean; a regression on `age`, `household_size`,\n`education_years` and `commute_min`; that regression plus a draw from `N(0, residual sd)` with\n`np.random.default_rng(0)`; and `KNNImputer(n_neighbors=5)` over those four columns and `rent`.\nScore each by RMSE against `truth_rent`, on the missing rows only.",
      shape="a Series of four RMSEs.",
      solution='''Rm = panel["rent"].isna().to_numpy()
XCOLS = ["age", "household_size", "education_years", "commute_min"]

def rmse(filled):
    return float(np.sqrt(np.mean((filled[Rm] - truth_rent[Rm]) ** 2)))


scores = {"mean": rmse(panel["rent"].fillna(panel["rent"].mean()).to_numpy())}

ols = sm.OLS(panel["rent"][~Rm], sm.add_constant(panel[XCOLS][~Rm])).fit()
pred = ols.predict(sm.add_constant(panel[XCOLS])).to_numpy()
scores["regression"] = rmse(np.where(Rm, pred, panel["rent"]))

rng2 = np.random.default_rng(0)
sd = float(np.sqrt(ols.mse_resid))
scores["stochastic regression"] = rmse(
    np.where(Rm, pred + rng2.normal(0, sd, len(panel)), panel["rent"]))

knn = KNNImputer(n_neighbors=5).fit_transform(panel[XCOLS + ["rent"]])
scores["knn k=5"] = rmse(knn[:, -1])

q9 = pd.Series(scores, name="rmse").round(0)
q9'''),
]
for q in Q:
    q["output"] = O[q["out"]]

build(dict(colab_path="data%20cleaning/practice/data_cleaning_worksheet.ipynb",
           pre=[("md", INTRO), ("code", SETUP), ("md", GIVEN_MD), ("code", GIVEN)],
           questions=Q),
      "/mnt/e/iitm course/da2402-26/data cleaning/practice/data_cleaning_worksheet.ipynb")
