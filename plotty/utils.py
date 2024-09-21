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
    def qpcr_cq(df: pd.DataFrame, ax: plt.Axes = False, **kwargs):
        """A helper function to measure & visualize cycle threshold (Cq) from qPCR data

        The input DataFrame 'df' only contains a single sample with a single target.
        If replicate present, average of replicate for Rn is calculated.
        """
        kws = {"cycle_bg": 10, "col_cycle": "cycle", "col_rn": "Rn", "well_loc": "well_position", 
            "color": "gray", "threshold_multiplier": 1.25, "linear_range": 7}
        for _k, _v in kwargs.items():
            if _k not in kws.keys():
                raise Exception(f"Error: Invalid kwargs '{_k}'. Accepted kwargs are {[_x for _x in kws.keys()]}")
            elif _k in kws.keys():
                kws[_k] = _v

        _df = df.copy()

        _replicate_avg = _df.groupby(df[kws["col_cycle"]])[kws["col_rn"]].mean()
        _replicate_avg = pd.DataFrame(_replicate_avg).reset_index()

        def measure_cq():
            _sampled_vals = _replicate_avg.head(kws["cycle_bg"])[kws["col_rn"]].to_list()
            _bg_val_avg = sum(_sampled_vals) / len(_sampled_vals) 
            _cq_signal = _bg_val_avg * kws["threshold_multiplier"]

            _linear_range = _replicate_avg.query(f" {kws['col_rn']} > {_cq_signal} ").head(7)
            _linear_range_rn = _linear_range[kws["col_rn"]].to_numpy()
            _linear_range_cycle = _linear_range[kws["col_cycle"]].to_numpy()

            _m, _c = np.polyfit(_linear_range_cycle, _linear_range_rn, 1)
            _cq_val = (_cq_signal - _c) / _m

            return _bg_val_avg, _cq_signal, _cq_val

        _m, _n, _q = measure_cq()

        if not ax:
            print(f"Background: {_m:.4f}, Cq: {_n:.3f} at Rn {_q:.3f}")
        else:
            ax.text(x=_q - 1, y = 3.5, s=f"Cq: {_q:.1f} ▶", ha="right", va="center", size=7, color=kws["color"])
            ax.axhline(y=_n, alpha=0.5, linewidth=0.9, linestyle=":", color=kws["color"])
            ax.axvline(x=_q, alpha=0.5, linewidth=0.9, linestyle=":", color=kws["color"])
