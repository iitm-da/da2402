import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm
from sklearn.impute import KNNImputer
from em_helper import em_mean_cov

D = "/mnt/e/iitm course/da2402-26/data cleaning/practice/data/"

def show(tag, v):
    print(f"@@{tag}"); print(repr(v)); print("@@end")

panel = pd.read_csv(D + "panel.csv")
NUM = ["age", "household_size", "education_years", "commute_min", "rent", "savings"]

# Q1  missingness patterns
q1 = panel[["rent", "savings", "power_backup"]].isna().value_counts()
show("q1", q1)

# Q2  group-mean comparison
R = panel["rent"].isna()
t, p = stats.ttest_ind(panel["age"][R], panel["age"][~R], equal_var=False)
q2 = (round(float(t), 3), float(f"{p:.3g}"))
show("q2", q2)

# Q3  permutation version, on the column believed MCAR
rng = np.random.default_rng(0)
age = panel["age"].to_numpy()
B = panel["power_backup"].isna()
obs = age[B].mean() - age[~B].mean()
null = np.empty(5000)
for i in range(5000):
    idx = rng.permutation(len(panel))
    null[i] = age[idx[:B.sum()]].mean() - age[idx[B.sum():]].mean()
q3 = (round(float(obs), 3), round(float((np.abs(null) >= abs(obs)).mean()), 4))
show("q3", q3)

# Q4  degrees of freedom by counting
patt = panel[NUM].notna().apply(tuple, axis=1)
slots = sum(sum(k) for k in patt.unique())
q4 = (len(patt.unique()), slots, slots - len(NUM))
show("q4", q4)

# Q5  Little's test
def littles_test(df, cols):
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
show("q5", q5)

# Q6  logistic on the missingness indicator, model-level LR test
PRED = ["age", "household_size", "education_years"]
def fit_logit(col):
    y = panel[col].isna().astype(int)
    X = sm.add_constant(panel[PRED])
    return sm.Logit(y, X).fit(disp=0)

m = fit_logit("rent")
lr = 2 * (m.llf - m.llnull)
q6 = (round(float(lr), 2), int(m.df_model), float(f"{m.llr_pvalue:.3g}"))
show("q6", q6)

# Q7  the Wald table
q7 = pd.DataFrame({"coef": m.params.round(4), "se": m.bse.round(4),
                   "OR": np.exp(m.params).round(3),
                   "p": m.pvalues.map(lambda v: float(f"{v:.3g}"))})
show("q7", q7)

# Q8  the same test on all three incomplete columns
q8 = pd.Series({c: float(f"{fit_logit(c).llr_pvalue:.3g}")
                for c in ["rent", "savings", "power_backup"]}, name="LR p")
show("q8", q8)

# Q9  imputation scoreboard on rent, against the held-out truth
truth_rent = np.load(D + "truth_rent.npy")
Rm = panel["rent"].isna().to_numpy()
XCOLS = ["age", "household_size", "education_years", "commute_min"]

def rmse(filled):
    return float(np.sqrt(np.mean((filled[Rm] - truth_rent[Rm]) ** 2)))

scores = {}
mean_fill = panel["rent"].fillna(panel["rent"].mean()).to_numpy()
scores["mean"] = rmse(mean_fill)

ols = sm.OLS(panel["rent"][~Rm], sm.add_constant(panel[XCOLS][~Rm])).fit()
pred = ols.predict(sm.add_constant(panel[XCOLS])).to_numpy()
reg_fill = np.where(Rm, pred, panel["rent"])
scores["regression"] = rmse(reg_fill)

rng2 = np.random.default_rng(0)
sd = float(np.sqrt(ols.mse_resid))
scores["stochastic regression"] = rmse(np.where(Rm, pred + rng2.normal(0, sd, len(panel)),
                                                panel["rent"]))

knn = KNNImputer(n_neighbors=5).fit_transform(panel[XCOLS + ["rent"]])
scores["knn k=5"] = rmse(knn[:, -1])

q9 = pd.Series(scores, name="rmse").round(0)
show("q9", q9)
