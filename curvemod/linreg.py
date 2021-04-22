# -------------------------------------------- #
# Aizan's linear regression class              #
# Modified from Erik Bern's tutorial           #
#  The hacker's guide to uncertainty estimates #
# -------------------------------------------- #

import random
import numpy as np
import scipy.optimize as opt


def linear_eq(x, m, c):
    """Function (or a model) to do linear equation; y = mx + c
    Also written as kx + m in some texts. Confusing, I know

    Params
      x: x value
      m: the slope
      c: y-intercept
    Returns y
    """
    return m * x + c


def l2_loss(tup, x, y):
    """L2 Loss function a.k.a least square errors (LS)

    Params
      tup: Using value from x0 (initial guess), see opt.minimize() block below.
           Unpacks into m and c
      x: The x-values
      y: The v-values
    """
    m, c = tup
    delta = linear_eq(x, m, c) - y  # Get the difference between actual and predicted
    return np.dot(delta, delta)     # Square that difference


class ConfInt:
    """Class for holding x, y, and n data to perform confidence interval by bootstrap resampling.

    Methods
      ConfInt.lin_reg(ax, points=False)
        Performing linear regression
      ConfInt.confidence_interval(ax, conf_curve=False, conf_band=True)
        Drawing confidence interval

    TODO:
      - Spit out R and P values (Person and Spearman), through a method, then draw legend
    """
    def __init__(self, x, y, n=250):
        """

        """
        self.x = np.array(x)
        self.y = np.array(y)
        self.n = n

    def lin_reg(self, ax, points=False):
        """Method for performing regression analysis and drawing the regression line

        Params
          ax     : The Axes object
          points : bool; draw the points (scatter plot), default False.

        TODO
          - Customization for the line
        """
        m_hat, c_hat = opt.minimize(l2_loss, x0=(0, 0), args=(self.x, self.y)).x
        ax.plot(self.x, linear_eq(self.x, m_hat, c_hat), color="cornflowerblue", linewidth=2.5, alpha=0.5)

        if points:
            ax.scatter(self.x, self.y, alpha=0.5, s=50)

    def confidence_interval(self, ax=None, conf_curve=False, conf_band=True):
        """Method for drawing confidence interval band and curves

        Params
          ax         : The Axes object
          conf_curve : bool; Draw confidence curves? Default to False
          conf_band  : bool; Draw confidence band? Default to True

        TODO
          Set confidence interval (99%, 95%, 90%)
        """
        xys = list(zip(self.x, self.y))
        curves = []

        # Calculate confidence interval by bootstrapping
        # The opt.minimize().x accesses the x portion of the returned value:
        #   an array of m & c in this case
        for i in range(self.n):
            bootstrap = [random.choice(xys) for _ in xys]
            bootstrap_x = np.array([x for x, y in bootstrap])
            bootstrap_y = np.array([y for x, y in bootstrap])
            m_hat, c_hat = opt.minimize(l2_loss, x0=(0, 0), args=(bootstrap_x, bootstrap_y)).x
            curves.append(linear_eq(self.x, m_hat, c_hat))

        # Plot individual confidence interval
        if conf_curve:
            for curve in curves:
                ax.plot(self.x, curve, alpha=0.1, linewidth=2, color="lightsteelblue")

        # Plot confidence interval band (97.5 -- 2.5 = 95%)
        # Sort them all with np.sort() so ax.fill_between() can properly work
        if conf_band:
            lo, hi = np.percentile(curves, (2.5, 97.5), axis=0)
            ax.fill_between(x=np.sort(self.x), y1=np.sort(lo), y2=np.sort(hi),
                            color="lightsteelblue", alpha=0.25)
