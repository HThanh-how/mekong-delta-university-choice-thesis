"""Recompute the thesis statistics from data/survey_486.csv.

Run from the repository root with Python 3. Dependencies: pandas, numpy,
scipy, statsmodels, and factor_analyzer.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import (
    calculate_bartlett_sphericity,
    calculate_kmo,
)
from scipy import stats
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "survey_486.csv"
FACTORS = ["FIT", "CAR", "REP", "COS", "SOC", "COM", "LOC", "DEC"]
PREDICTORS = FACTORS[:-1]


def item_columns(factor: str) -> list[str]:
    return [f"{factor}{index}" for index in range(1, 5)]


def cronbach_alpha(frame: pd.DataFrame) -> float:
    count = frame.shape[1]
    return float(
        count
        / (count - 1)
        * (1 - frame.var(ddof=1).sum() / frame.sum(axis=1).var(ddof=1))
    )


def corrected_item_total_min(frame: pd.DataFrame) -> float:
    values = [
        frame[column].corr(frame.drop(columns=column).sum(axis=1))
        for column in frame.columns
    ]
    return float(min(values))


def main() -> None:
    data = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    scores = pd.DataFrame(
        {factor: data[item_columns(factor)].mean(axis=1) for factor in FACTORS}
    )

    result: dict[str, object] = {
        "n": int(len(data)),
        "missing_values": int(data.isna().sum().sum()),
        "counts": {},
        "descriptives": {},
        "reliability": {},
    }

    for variable in ["GioiTinh", "KhuVuc", "ThuNhap"]:
        counts = data[variable].value_counts().sort_index()
        result["counts"][variable] = {
            str(code): {
                "n": int(value),
                "percent": float(100 * value / len(data)),
            }
            for code, value in counts.items()
        }

    for factor in FACTORS:
        frame = data[item_columns(factor)]
        result["descriptives"][factor] = {
            "mean": float(scores[factor].mean()),
            "sd": float(scores[factor].std(ddof=1)),
        }
        result["reliability"][factor] = {
            "alpha": cronbach_alpha(frame),
            "corrected_item_total_min": corrected_item_total_min(frame),
        }

    efa_data = data[[column for factor in PREDICTORS for column in item_columns(factor)]]
    kmo_items, kmo_total = calculate_kmo(efa_data)
    bartlett_chi2, bartlett_p = calculate_bartlett_sphericity(efa_data)
    efa = FactorAnalyzer(n_factors=7, rotation="promax", method="principal")
    efa.fit(efa_data)
    eigenvalues, _ = efa.get_eigenvalues()
    variance, proportional, cumulative = efa.get_factor_variance()
    loadings = pd.DataFrame(
        efa.loadings_, index=efa_data.columns, columns=[f"F{i}" for i in range(1, 8)]
    )
    result["efa"] = {
        "kmo": float(kmo_total),
        "bartlett_chi2": float(bartlett_chi2),
        "bartlett_df": 378,
        "bartlett_p": float(bartlett_p),
        "eigenvalues_first_7": [float(value) for value in eigenvalues[:7]],
        "variance_percent": [float(100 * value) for value in proportional],
        "cumulative_variance_percent": float(100 * cumulative[-1]),
        "loading_min_primary": float(loadings.abs().max(axis=1).min()),
        "loading_max_primary": float(loadings.abs().max(axis=1).max()),
        "loadings": loadings.round(6).to_dict(orient="index"),
    }

    x = sm.add_constant(scores[PREDICTORS])
    model = sm.OLS(scores["DEC"], x).fit()
    robust = model.get_robustcov_results(cov_type="HC3")
    standardized = (scores - scores.mean()) / scores.std(ddof=1)
    standardized_model = sm.OLS(
        standardized["DEC"], sm.add_constant(standardized[PREDICTORS])
    ).fit()
    vif = {
        predictor: float(variance_inflation_factor(x.values, index + 1))
        for index, predictor in enumerate(PREDICTORS)
    }
    influence = model.get_influence()
    cooks_distance = influence.cooks_distance[0]
    spearman_rho, spearman_p = stats.spearmanr(
        np.abs(model.resid), model.fittedvalues
    )
    bp_lm, bp_lm_p, bp_f, bp_f_p = het_breuschpagan(model.resid, x)
    result["regression"] = {
        "r2": float(model.rsquared),
        "adjusted_r2": float(model.rsquared_adj),
        "f": float(model.fvalue),
        "f_p": float(model.f_pvalue),
        "df_model": int(model.df_model),
        "df_resid": int(model.df_resid),
        "durbin_watson": float(durbin_watson(model.resid)),
        "max_cooks_distance": float(cooks_distance.max()),
        "spearman_abs_resid_fitted_rho": float(spearman_rho),
        "spearman_abs_resid_fitted_p": float(spearman_p),
        "breusch_pagan_f": float(bp_f),
        "breusch_pagan_f_p": float(bp_f_p),
        "coefficients": {
            name: {
                "b": float(model.params[name]),
                "se": float(model.bse[name]),
                "beta": float(standardized_model.params.get(name, 0.0)),
                "p": float(model.pvalues[name]),
                "vif": vif.get(name),
            }
            for name in model.params.index
        },
        "hc3": {
            name: {
                "se": float(robust.bse[index]),
                "p": float(robust.pvalues[index]),
            }
            for index, name in enumerate(model.params.index)
        },
    }

    area_groups = [
        scores.loc[data["KhuVuc"] == code, "LOC"] for code in sorted(data["KhuVuc"].unique())
    ]
    area_t, area_p = stats.ttest_ind(*area_groups, equal_var=False)
    income_groups = [
        scores.loc[data["ThuNhap"] == code, "COS"]
        for code in sorted(data["ThuNhap"].unique())
    ]
    income_f, income_p = stats.f_oneway(*income_groups)
    gender_groups = [
        scores.loc[data["GioiTinh"] == code, "DEC"]
        for code in sorted(data["GioiTinh"].unique())
    ]
    gender_f, gender_p = stats.f_oneway(*gender_groups)
    result["group_tests"] = {
        "loc_by_area": {
            "means": [float(group.mean()) for group in area_groups],
            "t": float(area_t),
            "p": float(area_p),
        },
        "cos_by_income": {
            "means": [float(group.mean()) for group in income_groups],
            "f": float(income_f),
            "p": float(income_p),
        },
        "dec_by_gender": {
            "means": [float(group.mean()) for group in gender_groups],
            "f": float(gender_f),
            "p": float(gender_p),
        },
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
