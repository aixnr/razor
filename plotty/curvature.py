import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class FourPL:
    """Assumes input as log2-transformed
    """
    bottom: float
    slope: float
    ic50: float
    top: float
    min_x: float
    max_x: float
    sample: Optional[str] = "Sample"
    n_points: Optional[int] = 100


def four_pl(x, a, b, c, d):
    """Formula for 4-parameter logistics
    Assumes untransformed input
    
    Parameters
    ----------
    x : list
      array of x values
    a : float
      bottom (a.k.a. minimum value)
    b : float
      slope
    c : float
      IC50 / EC50 / midpoint
    d : float
      top (a.k.a. maximum value)
    """
    return ((a - d) / (1.0 + ((x / c) ** b))) + d


def curvature(ax: plt.Axes, param: FourPL, color: str = "cornflowerblue", alpha: float = 1, zorder=-5) -> None:
    """Draws the 4-parameter sigmoidal line based on FourPL calculated elsewhere.
    This was necessary because curvemod.Sigmoid can be buggy and unusable on untransformed x values.

    Assumes untransformed input

    Parameters
    ----------
    ax : plt.Axes
    param : FourPL
    color : str
    alpha : float
    zorder : float
    """
    print(f"{param.sample} has an IC50 of {param.ic50:,.2f}")

    model_x = np.linspace(param.min_x, param.max_x, param.n_points)
    ax.plot(model_x, four_pl(model_x, param.bottom, param.slope, param.ic50, param.top),
            color=color, alpha=alpha, zorder=zorder)
