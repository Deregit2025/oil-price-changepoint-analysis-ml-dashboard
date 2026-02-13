# src/modelling/bayesian_cp_model.py

import pymc as pm
import numpy as np
import matplotlib.pyplot as plt

def bayesian_change_point_model(
    log_returns,
    draws=2000,
    tune=1000,
    target_accept=0.9,
    random_seed=42,
    downsample_step=None
):
    """
    Build and run a Bayesian Change Point model for a 1D time series of log returns.

    Parameters
    ----------
    log_returns : array-like
        The time series of log returns.
    draws : int
        Number of MCMC samples.
    tune : int
        Number of tuning steps.
    target_accept : float
        Target acceptance rate for NUTS sampler.
    random_seed : int
        Random seed for reproducibility.
    downsample_step : int, optional
        If set, use every N-th point for faster computation.

    Returns
    -------
    trace : pm.backends.base.MultiTrace
        The posterior samples from the model.
    model : pm.Model
        The PyMC model object.
    used_series : np.ndarray
        The series actually used (after optional downsampling).
    """
    try:
        log_returns = np.array(log_returns)
        if log_returns.ndim != 1:
            raise ValueError("log_returns must be a 1D array")

        # Downsample if requested
        if downsample_step is not None and downsample_step > 1:
            used_series = log_returns[::downsample_step]
        else:
            used_series = log_returns.copy()

        n_points = len(used_series)
        if n_points < 2:
            raise ValueError("Time series too short after downsampling")

    except Exception as e:
        raise RuntimeError(f"Input validation failed: {e}")

    # -----------------------------
    # Build Bayesian Change Point Model
    # -----------------------------
    with pm.Model() as model:
        # 1. Switch point
        tau = pm.DiscreteUniform("tau", lower=0, upper=n_points-1)

        # 2. Pre- and post-change means
        mu1 = pm.Normal("mu1", mu=0, sigma=0.05)
        mu2 = pm.Normal("mu2", mu=0, sigma=0.05)

        # 3. Shared standard deviation
        sigma = pm.HalfNormal("sigma", sigma=0.05)

        # 4. Likelihood with switch
        idx = np.arange(n_points)
        mu = pm.math.switch(tau >= idx, mu1, mu2)
        y_obs = pm.Normal("y_obs", mu=mu, sigma=sigma, observed=used_series)

        # 5. Sample posterior
        trace = pm.sample(
            draws=draws,
            tune=tune,
            random_seed=random_seed,
            target_accept=target_accept,
            cores=1
        )

    return trace, model, used_series


# -----------------------------
# Optional: Plot posterior distributions
# -----------------------------
def plot_trace(trace):
    """
    Plot trace and posterior distributions for tau, mu1, mu2, and sigma.
    """
    try:
        pm.plot_trace(trace)
        plt.show()
    except Exception as e:
        print(f"Trace plotting failed: {e}")


def plot_change_point_distribution(trace, dates):
    """
    Plot posterior distribution of tau over time series dates.

    Parameters
    ----------
    trace : pm.backends.base.MultiTrace
        The posterior samples
    dates : array-like
        Corresponding dates for the time series
    """
    try:
        tau_samples = trace.posterior["tau"].values.flatten()
        if len(tau_samples) != len(dates):
            # If downsampled, align with the actual used series length
            dates = dates[:len(tau_samples)]

        plt.figure(figsize=(14,5))
        plt.hist(dates[tau_samples], bins=50, color='orange', alpha=0.7)
        plt.title("Posterior Distribution of Change Point (tau)")
        plt.xlabel("Date")
        plt.ylabel("Frequency")
        plt.show()

    except Exception as e:
        print(f"Change point distribution plotting failed: {e}")
