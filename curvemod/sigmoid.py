# ------------------------------ #
# Aizan's curve fitting function #
# ------------------------------ #

import scipy.optimize as opt
import numpy as np
from matplotlib.ticker import ScalarFormatter


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
          ax        :
          fit       :
          points    :
          line_col  :
          point_col :
          log       :
        """
        min_x, max_x = np.amin(self.x_values), np.amax(self.x_values)
        model_x = np.linspace(min_x, max_x, 1000)
        ax.plot(model_x, four_pl(model_x, *fit), color=line_col)

        if log:
            ax.set_xscale("log", base=log)
            ax.xaxis.set_major_formatter(ScalarFormatter(useOffset=False))

        if points:
            ax.plot(self.x_values, self.y_values, marker="o", linestyle="", color=point_col)
