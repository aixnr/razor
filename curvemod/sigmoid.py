# --------------------------- #
# Aizan's curve fitting class #
# --------------------------- #

import scipy.optimize as opt
import numpy as np
from matplotlib.ticker import ScalarFormatter
from sklearn.metrics import r2_score
from scipy import interpolate


def four_pl(x, a, b, c, d):
    """Sigmoid 4 parameter logistic curve fit formula
    """
    return (a - b) / (1.0 + ((x / c) ** b)) + d


class Sigmoid:
    """Aizan's custom Sigmoid 4PL curve-fitting function.

    Import:
        from curvemod import Sigmoid

    General overview:
      1. Takes x (concentration or dilution) and y (readout) values at class initialization
         my_curve = Sigmoid(x, y)
      2. Draw the fitted curve
         my_curve.curve(ax=ax, fit=my_curve.fit())

    See individual methods for more information
    """
    def __init__(self, x, y):
        self.x_values = x
        self.y_values = y

    def __repr__(self):
        pass

    def fit(self):
        """Returning the 4 parameters as a list

        Return index (a list)
          0: (A) bottom
          1: (B) slope
          2: (C) Log IC50
          3: (D) top
        """
        params, params_cov = opt.curve_fit(four_pl, xdata=self.x_values, ydata=self.y_values, p0=[1, 1, 1, 1])
        return params

    def curve(self, ax, fit, points=False, line_col="black", point_col="gray", log=None):
        """Draw the fitted curve

        Params
          ax        : The Axes object to draw the plot on.
          fit       : Pass Sigmoid.fit() to this parameter.
          points    : bool; if True, draws points from actual data.
          line_col  : str; color for the line
          point_col : str; color for the points
          log       : int; if set to a number, will use that number as base to the log
        """
        min_x, max_x = np.amin(self.x_values), np.amax(self.x_values)
        model_x = np.linspace(min_x, max_x, 1000)
        ax.plot(model_x, four_pl(model_x, *fit), color=line_col)

        if log:
            ax.set_xscale("log", base=log)
            ax.xaxis.set_major_formatter(ScalarFormatter(useOffset=False))

        if points:
            ax.plot(self.x_values, self.y_values, marker="o", linestyle="", color=point_col)

    def r2(self, fit, ax=None):
        """Returns computed R-squared (coefficient of determination) value.

        Params:
          fit : Pass Sigmoid.fit() to this parameter.
          ax  : If supplied, with use the "legend" spot to indicate r2 value
        """
        r2 = r2_score(self.y_values, four_pl(self.x_values, *fit))

        if not ax:
            return print(f"r2: {round(r2, 3)}")
        if ax:
            ax.plot([], [], linestyle="", label=f"r2: {round(r2, 3)}")
            ax.legend()

    def spline(self, ax, color="silver"):
        """

        """
        # Run spline interpolation
        min_x, max_x = np.amin(self.x_values), np.amax(self.x_values)
        new_x = np.linspace(min_x, max_x, 1000)
        b_spline = interpolate.make_interp_spline(x=self.x_values, y=self.y_values)
        new_y = b_spline(new_x)

        ax.plot(new_x, new_y, alpha=0.5, color=color, linestyle="--")
        ax.plot(self.x_values, self.y_values, color=color, marker="o", linestyle="")
