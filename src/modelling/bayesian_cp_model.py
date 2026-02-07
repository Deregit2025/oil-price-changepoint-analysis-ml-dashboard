# src/modelling/bayesian_cp_model.py

import pymc as pm
import numpy as np
import matplotlib.pyplot as plt

def bayesian_change_point_model(log_returns, draws=2000, tune=1000, random_seed=42):
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
    random_seed : int
        Random seed for reproducibility.

    Returns
    -------
    trace : pm.backends.base.MultiTrace
        The posterior samples from the model.
    model : pm.Model
        The PyMC model object.
    """
    log_returns = np.array(log_returns)

    with pm.Model() as model:
        # -----------------------------
        # 1. Switch point (change point)
        # -----------------------------
        tau = pm.DiscreteUniform("tau", lower=0, upper=len(log_returns)-1)

        # -----------------------------
        # 2. Pre- and post-change means
        # -----------------------------
        mu1 = pm.Normal("mu1", mu=0, sigma=0.05)
        mu2 = pm.Normal("mu2", mu=0, sigma=0.05)

        # -----------------------------
        # 3. Shared standard deviation
        # -----------------------------
        sigma = pm.HalfNormal("sigma", sigma=0.05)

        # -----------------------------
        # 4. Likelihood using switch
        # -----------------------------
        idx = np.arange(len(log_returns))
        mu = pm.math.switch(tau >= idx, mu1, mu2)
        y_obs = pm.Normal("y_obs", mu=mu, sigma=sigma, observed=log_returns)

        # -----------------------------
        # 5. Sample posterior
        # -----------------------------
        trace = pm.sample(draws=draws, tune=tune, random_seed=random_seed, target_accept=0.95)

    return trace, model


# -----------------------------
# Optional: Plot posterior distributions
# -----------------------------
def plot_trace(trace):
    """
    Plot trace and posterior distributions for tau, mu1, mu2, and sigma.
    """
    pm.plot_trace(trace)
    plt.show()


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
    tau_samples = trace.posterior["tau"].values.flatten()
    plt.figure(figsize=(14,5))
    plt.hist(dates[tau_samples], bins=50, color='orange', alpha=0.7)
    plt.title("Posterior Distribution of Change Point (tau)")
    plt.xlabel("Date")
    plt.ylabel("Frequency")
    plt.show()
