import numpy as np, pandas as pd
from scipy import stats

def em_mean_cov(X, iters=300, tol=1e-8):
    """ML mean and covariance under missingness, by EM. X: (n, p) with NaN."""
    X = np.asarray(X, float)
    n, p = X.shape
    mu = np.nanmean(X, 0)
    S = np.cov(np.where(np.isnan(X), mu, X), rowvar=False)
    for _ in range(iters):
        T1 = np.zeros(p); T2 = np.zeros((p, p))
        for i in range(n):
            row = X[i]
            obs = ~np.isnan(row)
            mis = ~obs
            z = row.copy(); C = np.zeros((p, p))
            if mis.any():
                Soo = S[np.ix_(obs, obs)]; Smo = S[np.ix_(mis, obs)]
                B = Smo @ np.linalg.pinv(Soo)
                z[mis] = mu[mis] + B @ (row[obs] - mu[obs])
                C[np.ix_(mis, mis)] = S[np.ix_(mis, mis)] - B @ S[np.ix_(obs, mis)]
            T1 += z; T2 += np.outer(z, z) + C
        mu_new = T1 / n
        S_new = T2 / n - np.outer(mu_new, mu_new)
        if np.max(np.abs(mu_new - mu)) < tol and np.max(np.abs(S_new - S)) < tol:
            mu, S = mu_new, S_new
            break
        mu, S = mu_new, S_new
    return mu, S

def littles_test(df, cols):
    X = df[cols].to_numpy(float)
    mu, S = em_mean_cov(X)
    obs = ~np.isnan(X)
    d2 = 0.0; dfree = 0
    groups = {}
    for i, row in enumerate(obs):
        groups.setdefault(tuple(row), []).append(i)
    for key, idx in groups.items():
        J = np.array(key, bool)
        if not J.any():
            continue
        xbar = X[np.ix_(idx, np.where(J)[0])].mean(0)
        diff = xbar - mu[J]
        d2 += len(idx) * diff @ np.linalg.pinv(S[np.ix_(J, J)]) @ diff
        dfree += J.sum()
    dfree -= len(cols)
    return d2, int(dfree), float(stats.chi2.sf(d2, dfree))

if __name__ == "__main__":
    s = pd.read_csv("/mnt/e/iitm course/da2402-26/data cleaning/data/survey.csv")
    print("survey.csv 4 numeric:", littles_test(s, ["age","education_years","income","health_score"]))
    print("  slides say: 61.60 on 8 df, p = 2.27e-10")
