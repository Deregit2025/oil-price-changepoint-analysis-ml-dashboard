# src/modelling/bayesian_cp_model.py

import pymc as pm
import numpy as np
import matplotlib.pyplot as plt
import arviz as az


# -------------------------------------------------
# Bayesian Change Point Model
# -------------------------------------------------
def bayesian_change_point_model(
    log_returns,
    draws=1000,
    tune=1000,
    target_accept=0.95,
    random_seed=42
):
    """
    Bayesian Change Point model for 1D stationary time series.

    Parameters
    ----------
    log_returns : array-like
        Stationary time series (log returns).
    draws : int
        Number of posterior samples.
    tune : int
        Number of tuning steps.
    target_accept : float
        Target acceptance probability for NUTS sampler.
    random_seed : int
        Seed for reproducibility.

    Returns
    -------
    trace : arviz.InferenceData
        Posterior samples.
    model : pymc.Model
        PyMC model object.
    """

    # -----------------------------
    # Input Validation
    # -----------------------------
    if log_returns is None:
        raise ValueError("log_returns cannot be None")

    log_returns = np.asarray(log_returns)

    if log_returns.ndim != 1:
        raise ValueError("log_returns must be a 1D array")

    if len(log_returns) < 10:
        raise ValueError("Time series too short for change point detection")

    if np.isnan(log_returns).any():
        raise ValueError("log_returns contains NaN values")

    n = len(log_returns)

    try:
        with pm.Model() as model:

            # Change point location
            tau = pm.DiscreteUniform("tau", lower=0, upper=n - 1)

            # Means before and after change
            mu1 = pm.Normal("mu1", mu=0, sigma=1)
            mu2 = pm.Normal("mu2", mu=0, sigma=1)

            # Shared noise
            sigma = pm.HalfNormal("sigma", sigma=1)

            # Mean switching logic
            idx = np.arange(n)
            mu = pm.math.switch(tau >= idx, mu1, mu2)

            # Likelihood
            pm.Normal("obs", mu=mu, sigma=sigma, observed=log_returns)

            # Sampling
            trace = pm.sample(
                draws=draws,
                tune=tune,
                target_accept=target_accept,
                random_seed=random_seed,
                return_inferencedata=True,
                progressbar=True
            )

    except Exception as e:
        raise RuntimeError(f"Bayesian model sampling failed: {e}")

    return trace, model


# -------------------------------------------------
# Diagnostics: Trace Plot
# -------------------------------------------------
def plot_trace(trace):
    """
    Plot posterior traces for parameters.
    """
    if trace is None:
        raise ValueError("trace cannot be None")

    try:
        az.plot_trace(trace)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        raise RuntimeError(f"Trace plotting failed: {e}")


# -------------------------------------------------
# Diagnostics: Change Point Distribution
# -------------------------------------------------
def plot_change_point_distribution(trace, dates):
    """
    Visualize posterior distribution of change point.

    Parameters
    ----------
    trace : arviz.InferenceData
    dates : array-like
        Date index corresponding to series
    """

    if trace is None:
        raise ValueError("trace cannot be None")

    try:
        tau_samples = trace.posterior["tau"].values.flatten()

        plt.figure(figsize=(14, 5))
        plt.hist(dates[tau_samples], bins=50)
        plt.title("Posterior Distribution of Change Point (tau)")
        plt.xlabel("Date")
        plt.ylabel("Frequency")
        plt.grid(True)
        plt.show()

    except Exception as e:
        raise RuntimeError(f"Change point distribution plot failed: {e}")
