"""
bayesian_cp_model.py

Bayesian Change Point model for Brent oil prices.
Uses PyMC for probabilistic modeling and MCMC sampling.
Optimized for runtime (<5 min for weekly aggregated data).
"""

import pymc as pm
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def run_bayesian_change_point_model(
    log_returns: np.ndarray,
    draws: int = 1000,      # smaller number of posterior samples
    tune: int = 500,        # shorter tuning
    chains: int = 2,        # fewer chains
    target_accept: float = 0.9,
    random_seed: int = 42
) -> dict:
    """
    Run a Bayesian change point model on log returns.

    Model: Two-regime mean with a single switch point (tau)

    Parameters
    ----------
    log_returns : np.ndarray
        Array of log returns
    draws : int
        Number of MCMC draws
    tune : int
        Number of tuning steps
    chains : int
        Number of chains
    target_accept : float
        Target acceptance rate for NUTS sampler
    random_seed : int
        Random seed for reproducibility

    Returns
    -------
    dict
        trace: PyMC trace
        summary: posterior summary table
        tau_posterior: samples of change point index
    """
    try:
        n = len(log_returns)
        logger.info("Running Bayesian Change Point Model on %d observations", n)

        with pm.Model() as model:

            # Prior for change point: uniform discrete
            tau = pm.DiscreteUniform("tau", lower=0, upper=n - 1)

            # Priors for means before/after change point
            mu_1 = pm.Normal("mu_1", mu=0, sigma=0.05)
            mu_2 = pm.Normal("mu_2", mu=0, sigma=0.05)

            # Prior for volatility
            sigma = pm.HalfNormal("sigma", sigma=0.05)

            # Switch function: use pm.math.switch
            mu = pm.math.switch(tau >= np.arange(n), mu_1, mu_2)

            # Likelihood
            obs = pm.Normal("obs", mu=mu, sigma=sigma, observed=log_returns)

            # Sample
            trace = pm.sample(
                draws=draws,
                tune=tune,
                chains=chains,
                target_accept=target_accept,
                random_seed=random_seed,
                progressbar=True,
                cores=1  # single core to avoid Jupyter crash
            )

        # Posterior summary
        summary = pm.summary(trace)
        tau_samples = trace.posterior["tau"].values.flatten()

        logger.info("Model sampling completed successfully")
        return {
            "trace": trace,
            "summary": summary,
            "tau_posterior": tau_samples
        }

    except Exception as e:
        logger.exception("Failed running Bayesian Change Point Model")
        raise
