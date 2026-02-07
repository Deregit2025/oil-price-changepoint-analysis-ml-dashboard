# **Change Point Model Overview**

## What is a Change Point?

A **change point** is a point in a time series where the statistical properties of the data (e.g., mean or variance) shift.
In the context of Brent oil prices, a change point represents a **structural change in price behavior** that may correspond to significant geopolitical, economic, or policy events.

**Key points:**

* Before the change point: the series follows one regime (e.g., stable mean/variance)
* After the change point: the series shifts to a different regime
* Multiple change points can occur over time, but for simplicity, we detect **major structural changes**

---

## Bayesian Change Point Modeling

We use **Bayesian inference** to estimate change points probabilistically.

### Model Components

1. **Switch Point (τ)**

   * Represents the unknown date where the change occurs
   * Modeled as a **discrete uniform prior** over all dates in the dataset

2. **Parameters Before/After (μ₁, μ₂)**

   * Mean log return before and after the change point
   * Captures the magnitude and direction of the price shift

3. **Likelihood**

   * Observed log returns are modeled as normally distributed around the current mean
   * Uses `pm.Normal` with mean = μ₁ or μ₂ depending on τ

4. **Switch Function**

   * `pm.math.switch` selects μ₁ or μ₂ for each time point based on whether t < τ or t ≥ τ

5. **Sampler (MCMC)**

   * We sample from the **posterior distribution** using Markov Chain Monte Carlo (MCMC)
   * Provides probabilistic estimates of τ, μ₁, μ₂

---

## Expected Outputs

* **Posterior of τ** → distribution of likely change point dates
* **Posterior of μ₁, μ₂** → estimated mean log returns before and after the change
* **Probabilistic statements** → e.g., "There is a 95% probability that a major structural shift occurred around [Date]"

**Interpretation:**

* Narrow posterior → high certainty of change point
* Wide posterior → uncertainty about timing
* Magnitude of μ₂ − μ₁ → strength of impact on prices

---

## Why Bayesian?

* Provides a **full probability distribution** over possible change points, not just a single estimate
* Incorporates **prior knowledge** if available
* Quantifies **uncertainty**, which is crucial for investors and policymakers
* Fits naturally into a **data-driven, evidence-based analytical workflow**



