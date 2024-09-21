import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Optional
from plotty import PlotUtils as PU
from plotty import FourPL, curvature, SpecificHill, specific_hill_curve

marker_kws: dict = {
    "marker": "o",
    "markersize": "7.5",
    "markeredgewidth": "1.5",
    "markeredgecolor": "black",
}


class DilutionCurve:
    def __init__(self, data: pd.DataFrame, sample: str, color="cornflowerblue"):
        self.data = data.query(f" Sample == '{sample}' ").reset_index(drop=True)
        self.sample = sample
        self.marker_kws = marker_kws
        self.color = color

    def parameters(
        self,
        concentration: list,
        concentration_range: list,
        concentration_exponent: list,
        dilution_range: range,
        min_x: int,
        max_x: int,
    ):
        self.conc = concentration
        self.conc_range = concentration_range
        self.conc_exponent = concentration_exponent
        self.range = dilution_range
        self.min_x, self.max_x = min_x, max_x

        return self

    def plot(self, ax: plt.Axes, log=True, base=10):
        self.ax = ax

        _cols_avg = [f"Avg_{x}" for x in self.range]
        _cols_sd = [f"SD_{x}" for x in self.range]

        _avg = self.data[_cols_avg].to_numpy().flatten()
        _sd = self.data[_cols_sd].to_numpy().flatten()

        for _x, _y, _v in zip(self.conc, _avg, _sd):
            ax.plot(_x, _y, color=self.color, linestyle="", **self.marker_kws)
            ax.vlines(_x, ymin=_y - _v, ymax=_y + _v, color=self.color, zorder=-5)

        if log:
            PU.log_scale(ax=ax, axis="x", base=base)

        ax.set_xticks(self.conc_range, [x for x in self.conc_exponent], fontsize=9)

        return self

    def fit_4pl(self):
        """Performs four-parameter logistic fitting"""
        _cols_fourpl = ["bottom", "slope", "ic50", "top"]
        _fourpl = self.data[_cols_fourpl].to_numpy().flatten()
        _bottom, _slope, _ic50, _top = _fourpl[0], _fourpl[1], _fourpl[2], _fourpl[3]

        _4pl_class = FourPL(
            _bottom,
            _slope,
            _ic50,
            _top,
            min_x=self.min_x,
            max_x=self.max_x,
            sample=self.sample,
        )
        curvature(self.ax, _4pl_class, color=self.color)

        return self

    def fit_shc(self):
        """Performs specific binding with hill slope curving"""
        _cols_sh = ["bmax", "h", "kd"]
        _sh = self.data[_cols_sh].to_numpy().flatten()
        _bmax, _h, _kd = _sh[0], _sh[1], _sh[2]

        _sh_class = SpecificHill(_bmax, _h, _kd, min_x=self.min_x, max_x=self.max_x)
        specific_hill_curve(ax=self.ax, param=_sh_class, color=self.color)

        return self

    @staticmethod
    def dummy_legend(
        ax: plt.Axes, sample: str, color: str = "cornflowerblue", ec50: Optional[float] = False
    ):
        if ec50:
            ax.plot([], [], label=f"{sample} ({ec50})", color=color, **marker_kws)
        else:
            ax.plot([], [], label=f"{sample}", color=color, **marker_kws)

    @staticmethod
    def prettify(
        ax: plt.Axes,
        ylim_top: float,
        ylim_bottom: float,
        ylim_interval: float,
        base: int = 10,
    ):
        ax.spines[["top", "right"]].set_visible(False)

        for y in np.arange(ylim_bottom, ylim_top, ylim_interval):
            ax.axhline(
                y=y,
                color="silver",
                linestyle="--",
                linewidth=0.5,
                alpha=1 / 3,
                zorder=-10,
            )
