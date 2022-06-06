# ----------------------------------------------------------- #
# Aizan's Lowess class for performing LOWESS analysis         #
# Confidence interval included, generated using bootstrapping #
# Inspired by:                                                #
#   https://james-brennan.github.io/posts/lowess_conf/        #
# ----------------------------------------------------------- #

import numpy as np
from statsmodels.nonparametric.smoothers_lowess import lowess as sm_lowess
from scipy import interpolate, stats
import warnings


def data_example(ax=None):
    """Example data to perform the LOWESS on
    """
    x = 5 * np.random.random(100)
    y = np.sin(x) * 3 * np.exp(-x) + np.random.normal(0, 0.2, 100)

    if not ax:
        return x, y
    if ax:
        ax.plot(x, y, 'k.')


def smooth(x, y, grid_x):
    """Smoother function
    This function samples 50% of the observations and fits the lowess model.
    This function is run K times (default=100), hence it has inherent stochasticity.
    """
    _samples = np.random.choice(len(x), size=50, replace=True)
    _sample_y = y[_samples]
    _sample_x = x[_samples]

    # Perform LOWESS
    _sm_y = sm_lowess(endog=_sample_y, exog=_sample_x,
                      frac=1. / 5., it=5, return_sorted=False)

    # Regularly sample it onto the grid
    grid_y = interpolate.interp1d(x=_sample_x, y=_sm_y, fill_value="extrapolate")(grid_x)

    return grid_y


class Lowess:
    def __init__(self, x, y):
        """Lowess class requires x and y
        """
        self._x = x
        self._y = y

    def plot(self, ax):
        ax.plot(self._x, self._y, 'k.')

    def fit(self, ax=None, color="tomato", alpha=0.75, linestyle="-"):
        """Fit a LOWESS line using the lowess function from statsmodels
        """
        sm_x, sm_y = sm_lowess(endog=self._y, exog=self._x,
                               frac=1. / 5., it=5, return_sorted=True).T

        if not ax:
            return sm_x, sm_y
        if ax:
            ax.plot(sm_x, sm_y, color=color, alpha=alpha, linestyle=linestyle)

    def conf_int(self, ax=None, K=100, band=None, **kwargs):
        """Calculate and draw confidence intervals

        Params:
          ax       : Axes object to draw chart on
          K        : int; number of interaction. Default = 100
          band     : str; show band as either "lines" or "percentile"
          **kwargs : Named parameters, see below

        Default parameters for **kwargs:
          color    :
          alpha    :
          interval :
        """

        # kwargs for additional parameters
        kws = {"color": "steelblue", "alpha": 0.1, "interval": 95}

        # Re-assign kws from kwargs when needed
        for _key, _value in kwargs.items():
            if _key not in kws.keys():
                raise Exception(f"Error: Invalid kwargs '{_key}'. Accepted **kwargs are {[x for x in kws.keys()]}")
            if _key in kws.keys():
                kws[_key] = _value

        # Set the lower and upper bound for confidence interval to use with band
        _interval = (100 - kws["interval"]) / 2
        _int_bottom, _int_top = (0 + _interval, 100 - _interval)

        # Suppress scipy's RuntimeWarning (interpolate.py), related to true_divide
        warnings.filterwarnings("ignore")

        # Make my life easier with shorter object name
        _x = self._x
        _y = self._y

        # Perform 'smoothing'
        grid_x = np.linspace(_x.min(), _x.max())
        _smooths = np.stack([smooth(_x, _y, grid_x) for k in range(K)]).T

        if not band:
            return _smooths

        if band:
            if band == "lines":
                # Drawing lines instead of band is not preferred.
                ax.plot(grid_x, _smooths, color=kws["color"], alpha=kws["alpha"])

            elif band == "percentile":
                # This is a percentile-based confidence interval.
                # This is possible since bootstrapping provides draws from the posterior of the LOWESS smooth.
                _lo, _hi = np.nanpercentile(_smooths, (_int_bottom, _int_top), axis=1)
                ax.fill_between(x=grid_x, y1=_lo, y2=_hi, alpha=kws["alpha"], color=kws["color"])

            elif band == "se":
                # Alternative, draw confidence interval using µ + (z-score)σ
                # e.g. 97.5 percentile translates into a z-score of ~1.96
                _percentile = kws["interval"] / 100
                _zscore = stats.norm.ppf(_percentile)

                # Calculate mean and stderr
                _mean = np.nanmean(_smooths, axis=1)
                _stderr = stats.sem(_smooths, axis=1)
                _stderr = np.nanstd(_smooths, axis=1, ddof=0)

                # Plot
                ax.fill_between(grid_x, _mean - _zscore * _stderr, _mean + _zscore * _stderr,
                                alpha=kws["alpha"], color=kws["color"])

            else:
                raise Exception("Invalid band description; use either 'lines', 'se', or 'percentile'")
