from typing import Union, Tuple
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import matplotlib.patches as patches
import pandas as pd
import numpy as np


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

    @staticmethod
    def png(fig: plt.Figure, path: str, dpi: int = 300):
        fig.savefig(path, format="png", dpi=dpi, bbox_inches="tight")

    @staticmethod
    def fontsize_labels(ax: plt.Axes, axis: str, size: float) -> None:
        if axis == "x":
            ax.xaxis.label.set_size(size)
        elif axis == "y":
            ax.yaxis.label.set_size(size)
        elif axis == "both":
            ax.xaxis.label.set_size(size)
            ax.yaxis.label.set_size(size)

    @staticmethod
    def fontsize_ticks(ax: plt.Axes, axis: str, size: float) -> None:
        if axis == "x":
            for label in ax.get_xticklabels():
                label.set_fontsize(size)
        if axis == "y":
            for label in ax.get_yticklabels():
                label.set_fontsize(size)
        elif axis == "both":
            for label in ax.get_xticklabels():
                label.set_fontsize(size)
            for label in ax.get_yticklabels():
                label.set_fontsize(size)

    @staticmethod
    def ticks_formatter(ax: plt.Axes, axis: str, param: tuple[float, float, float], p: int = 0) -> None:
        """
        Parameters
        ----------
        param : tuple[float, float, float]
            Values to be unpacked into np.arange() for setting the range.
        p : int
            Precision, i.e. how many decimal points. Defaults = 0 decimal point.
        """
        ticks = np.arange(*param)
        if axis == "x":
            ax.set_xticks(ticks)
            ax.set_xticklabels([f"{n:,.{p}f}" for n in ticks])
        if axis == "y":
            ax.set_yticks(ticks)
            ax.set_yticklabels([f"{n:,.{p}f}" for n in ticks])
        if axis == "both":
            ax.set_xticks(ticks)
            ax.set_xticklabels([f"{n:,.{p}f}" for n in ticks])
            ax.set_yticks(ticks)
            ax.set_yticklabels([f"{n:,.{p}f}" for n in ticks])
