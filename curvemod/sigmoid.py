"""
Sigmoid four-parameter logistic curve fitting

Usage:
  from curvemod import Sigmoid
  fourpl = Sigmoid(x, y).fit()
  fourpl.curve(ax=ax)
  fourpl.r2(ax=ax)
  fourpl.mid(ax=ax)
"""
from typing import Union
import scipy.optimize as opt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from sklearn.metrics import r2_score


def four_pl(x, a, b, c, d):
    """Sigmoid 4 parameter logistic curve fit formula

    Note (16 Oct 2022): Different form of 4PL might generate an *interesting* error.
    """
    # return (a - b) / (1.0 + ((x / c) ** b)) + d
    return ((a - d) / (1.0 + ((x / c) ** b))) + d


class Sigmoid:
    def __init__(self, x: list, y: list, start_conc: float = None, dilution: list = None):
        """
        Params
        ======
          x          : x-values (independent variable, e.g., concentration)
          y          : y-values (readout, e.g., OD450nm from ELISA)
          start_conc :
          dilution   :
          conc_list  :  Calculate two-fold down, log10-transformed of the start_conc (7 dilution points)
        """
        self.x_values = x
        self.y_values = y
        self.start_conc = start_conc
        self.dilution = dilution
        self.conc_list = []

    def fit(self, pretty: bool = False) -> None:
        """
        Params
        ======
          pretty: prettify the print output for human
        """
        params, _ = opt.curve_fit(four_pl, xdata=self.x_values, ydata=self.y_values, p0=[1, 1, 1, 1], maxfev=5000)
        self.params = params

        if not pretty:
            return self
        elif pretty:
            print("(A) Bottom: {0:.3f}, (B) Slope: {1:.3f}, (C) IC50: {2:.4f}, (D) Top: {3:.3f}".format(*params))
            print(f"LogIC50: {round(np.log10(params[2]), 3)}")
        else:
            raise Exception("Error!")

    def curve(self, ax: plt.Axes, points=False, line_col="black", point_col="gray",
              log: int = None, n_points=1000, alpha=0.5, spacing="geometric") -> None:
        """Draw the fitted curve

        Params
          points    : if True, draws points from actual data.
          line_col  : color for the line
          point_col : color for the points
          log       : if set to a number, will use that number as base to the log
          n_points  : number of points for the np.linspace to generate
          alpha     : alpha transparency value for the curve
        """
        min_x, max_x = np.amin(self.x_values), np.amax(self.x_values)

        if spacing == "linear":
            model_x = np.linspace(min_x, max_x, n_points)
        elif spacing == "geometric":
            model_x = np.geomspace(min_x, max_x, n_points)
        else:
            raise Exception("Invalid value for the 'spacing' parameter")

        ax.plot(model_x, four_pl(model_x, *self.params), color=line_col, alpha=alpha)

        if log:
            ax.set_xscale("log", base=log)
            ax.xaxis.set_major_formatter(ScalarFormatter(useOffset=False))

        if points:
            ax.plot(self.x_values, self.y_values, marker="o", linestyle="", color=point_col)

    def r2(self, ax: plt.Axes = None) -> Union[float, None]:
        """Returns computed R-squared (coefficient of determination) value.
        """
        r2 = r2_score(self.y_values, four_pl(self.x_values, *self.params))

        if not ax:
            return r2
        if ax:
            _r2_text = r"R$^{2}$"
            ax.plot([], [], linestyle="", label=f"{_r2_text}: {round(r2, 5)}")
            ax.legend(frameon=False)

    def mid(self, ax: plt.Axes = False, color="gray") -> None:
        """Show the midpoint on the curve
        """
        _x_ic50 = self.params[2]
        _y_mid = four_pl(_x_ic50, *self.params)

        if not ax:
            print({"IC50": _x_ic50, "y": _y_mid})
        else:
            plot_kwargs = {"linestyle": "--", "linewidth": 1, "alpha": 0.4, "color": color}
            min_x_left = ax.get_xlim()[0]
            min_y_bottom = ax.get_ylim()[0]
            ax.hlines(xmin=min_x_left, xmax=_x_ic50, y=_y_mid, **plot_kwargs)
            ax.vlines(ymin=min_y_bottom, ymax=_y_mid, x=_x_ic50, **plot_kwargs)
