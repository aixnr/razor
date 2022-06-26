"""New LOWESS constructor class

Date created: 25JUN2022
Date updated: 25JUN2022

Created to replace lowess.py with the same API.
Cleaner code, cleaner API.
Using official LOWESS Smoother tutorial on statsmodels website.

Constraints:
  - For better visualization, ensure y values are log-transformed.
  - The parameter frac is now set at 0.5 (50%) for estimating each y-value.
  - The parameter xval is used to ensure smoother line
"""

import numpy as np
import statsmodels.api as sm


class Lowess:
    def __init__(self, x, y, K=100):
        """Class constructor
        Default bootstrap iteration is K=100.
        xvals list is generated for evaluating regressions, with length of K
        """
        self._x = x
        self._y = y
        self._K = K

        self._xvals = np.linspace(x.min(), x.max(), K)

    def fit(self, ax=None, color="tomato", alpha=0.75, linestyle="-", frac=0.5):
        """Fit a LOWESS curve and draw
        Default fraction of data to estimate y-value is 0.5 (50%).
        High frac value = smoother curve.
        """
        # Save to self
        self._frac = frac

        # Perform LOWESS
        _smoothed = sm.nonparametric.lowess(exog=self._x, endog=self._y, xvals=self._xvals, frac=self._frac)

        if not ax:
            return _smoothed
        elif ax:
            ax.plot(self._xvals, _smoothed, color=color, alpha=alpha, linestyle=linestyle)

    def conf_int(self, ax=None, interval=0.95, color="steelblue", alpha=0.1):
        """Draw confidence interval
        """
        # Perform bootstrap resampling of the data
        # and evaluate smoothing at a fixed set of points
        _smoothed_values = np.empty((self._K, len(self._xvals)))
        for _i in range(self._K):
            _sample = np.random.choice(len(self._x), len(self._x), replace=True)
            _sampled_x = self._x[_sample]
            _sampled_y = self._y[_sample]

            _smoothed_values[_i] = sm.nonparametric.lowess(exog=_sampled_x, endog=_sampled_y, xvals=self._xvals, frac=self._frac)

        # Get confidence interval
        _sorted_values = np.sort(_smoothed_values, axis=0)
        _bound = int(self._K * (1 - interval) / 2)
        _bottom = _sorted_values[_bound - 1]
        _top = _sorted_values[- _bound]

        if not ax:
            return _bottom, _top

        if ax:
            ax.fill_between(self._xvals, _bottom, _top, color=color, alpha=alpha)
