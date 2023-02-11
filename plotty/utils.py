from typing import Union, Tuple
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import matplotlib.patches as patches


class PlotUtils:
    @staticmethod
    def starsig(value: float) -> str:
        if value > 0.05:
            return "ns"
        elif 0.05 >= value > 0.01:
            return "*"
        elif 0.01 >= value > 0.001:
            return "**"
        elif 0.001 >= value > 0.0001:
            return "***"
        elif value <= 0.0001:
            return "****"

    @staticmethod
    def log_scale(ax: plt.Axes, axis: str, base: int) -> None:
        if axis == "x":
            ax.set_xscale("log", base=base)
            ax.xaxis.set_major_formatter(ScalarFormatter(useOffset=False))
            ax.ticklabel_format(style="plain", axis=axis)
        elif axis == "y":
            ax.set_yscale("log", base=base)
            ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
            ax.ticklabel_format(style="plain", axis=axis)
        else:
            raise Exception("The 'axis' param only accepts 'x' or 'y'")

    @staticmethod
    def lod_rectangle(ax: plt.Axes,
                      xy: Union[Tuple[float, float], None] = None,
                      width: Union[float, None] = None, height: float = 0,
                      facecolor="gray", alpha=0.4) -> None:

        if not xy:
            xy = (ax.get_xlim()[0], ax.get_ylim()[0])
        
        if not width:
            width = ax.get_xlim()[1] - ax.get_xlim()[0]

        _rect = patches.Rectangle(xy=xy, width=width, height=height, facecolor=facecolor, alpha=alpha)
        ax.add_patch(_rect)
