# ------------------------------------------------ #
# Better heatmap with heatermap                    #
# With option to encode visualization for p-values #
# Inspired by heatmapz package                     #
# ------------------------------------------------ #

# Import required modules
import pandas as pd
import seaborn as sns
import numpy as np
from scipy import stats


def palette(x=None, user="plotter"):
    """Public function to assign color to value

    Use this function with default value for "user" parameter when plotting
      to apply to the color to each value with .apply()

    For making the colorbar, run with user="colormap"
    """
    # Use 256 color steps between -1 and 1 (range for the correlation values)
    _n_colors = 256

    # Default val of 96 for the size of the intermediate region
    # so that the color picks up right below r value of 0.5 for either direction
    _intermediate_region = 96

    # Define palette with n_colors and _intermediate_region
    _palette = sns.diverging_palette(240, 10, n=_n_colors, sep=_intermediate_region)
    _color_min, _color_max = [-1, 1]

    # Sub-function to perform color mapping
    def value_to_color(value=x):
        _value_position = float((value - _color_min) / (_color_max - _color_min))
        _index = int(_value_position * (_n_colors - 1))
        return _palette[_index]

    # Execute
    if user == "plotter":
        return value_to_color(x)
    elif user == "colormap":
        return _palette, np.linspace(_color_min, _color_max, _n_colors)


def colorbar(ax, scale_spacing=3):
    """Create colorbar
    Assuming that the whole heatmap was created with a GridSpec

    # Instantiate the drawing canvas
    fig = plt.figure()
    gs = fig.add_gridspec(1, 16)       # Create 16-column gridspec
    ax1 = fig.add_subplot(gs[:, :-2])  # Reserve 1 -- 14 for the main heatmap
    ax2 = fig.add_subplot(gs[:, -1])   # Reserve 16 for the colorbar

    # Draw the heatmap
    Heatermap(df).plotter(ax=ax1, size_scale, method, shape)
    colormap(ax2)
    """
    # Access palette information
    _palette, _bar_y = palette(user="colormap")

    # Plot the bar chart with Axes.barh()
    ax.barh(
        y=_bar_y,                     # The y values
        width=5,                      # Width (size) of the bar chart
        color=_palette,               # The color
        height=_bar_y[1] - _bar_y[0]  # Clip the height
    )

    # Fine customization
    ax.set_title(r"$R$")
    ax.set_xlim(1, 2)                                        # Clip x-axis
    ax.grid(False)
    ax.set_facecolor("white")
    ax.set_xticks([])                                                    # Remove x-ticks
    ax.set_yticks(np.linspace(min(_bar_y), max(_bar_y), scale_spacing))  # Show y-tick at n of scale_spacing
    ax.yaxis.tick_right()
    for sp in ["top", "right", "bottom", "left"]:
        ax.spines[sp].set_visible(False)


class Heatermap:
    """Heatermap class
    """

    def __init__(self, data):
        self.data = data.copy()

    def corr(self, method="pearson", p_value=False):
        """
        Parameters
          methods :
          p_value :
        """
        # Create a correlation matrix with pd.corr()
        _corr_df = self.data.corr(method=method)

        # Reset index without dropping, then melt as into 3-columns DataFrame
        _corr_df = _corr_df.reset_index().rename(columns={"index": "feature_x"})
        _melted_df = pd.melt(_corr_df, id_vars="feature_x", var_name="feature_y", value_name="corr")

        # Function to calculate for p-value
        def calculate_p_value(data, corr_method=method):
            if corr_method == "pearson":
                _stat = stats.pearsonr
            elif corr_method == "spearman":
                _stat = stats.spearmanr
            else:
                raise Exception("Only accepts pearson or spearman for now; kendall not supported")

            # Extract names for feature from feature_x and feature_y column into list
            _feature_x = data["feature_x"].to_list()
            _feature_y = data["feature_y"].to_list()

            # Catch the computed p-value later
            _p_val_list = []

            # Loop to perform p-value calculation
            for _x, _y in zip(_feature_x, _feature_y):
                # Using column names (_x and _y) to extract data as pd.Series
                _x_value = self.data[_x]
                _y_value = self.data[_y]

                # Perform stats
                _p_val = _stat(_x_value, _y_value)[1]  # p-value at index of 1
                _p_val_list.append(round(_p_val, 3))   # Append and round to 3 decimal places

            data["p-value"] = _p_val_list              # Dump the p-values into "p-value" column

            return data

        if not p_value:
            return _melted_df
        elif p_value:
            return calculate_p_value(_melted_df)

    def plotter(self, ax=None, size_scale=500, label_size=12,
                method="pearson", shape="s", feature_order=None):
        """Plot the correlation heatmap

        Parameters
          ax            : Axes object
          size_scale    : int; Set the size for the marker. Increase or decrease whenever needed
          label_size    : int; Set font size for the x- and y-axis labels
          method        : str; Correlation calculation method, either 'pearson' or 'spearman'
          shape         : str; Shape of the marker, 's' for square, 'o' for circle
          feature_order : list; Override the order for the x- and y-labels with manual ordering
        """
        # Perform correlation
        _df = self.corr(method=method, p_value=True)

        # Reduce the marker's opacity when p-value > 0.051 (not significant)
        _df["alpha"] = _df["p-value"].apply(lambda x: 0.25 if x > 0.051 else 1.0)

        # Reduce the marker's size where R-value is -0.5 < x < 0.5 due to weak correlation
        _df["size"] = _df["corr"].apply(lambda x: 0.4 * size_scale if abs(x) < 0.5 else size_scale)

        # Label for x is ascending, label for y is descending
        if not feature_order:
            _x_label = sorted([x for x in _df["feature_x"].unique()])
            _y_label = sorted([y for y in _df["feature_y"].unique()], reverse=True)
        elif feature_order:
            _x_label = [x for x in feature_order]          # Retain ordering
            _y_label = [y for y in feature_order[::-1]]    # Reverse the ordering with [::-1] slice

        # Map number to label with enumerate(), to be used when calling ax.scatter()
        _x_label_numeric = {e[1]: e[0] for e in enumerate(_x_label)}
        _y_label_numeric = {e[1]: e[0] for e in enumerate(_y_label)}

        if ax:
            # Plot; labels on both axes are numeric with the use of .map() method on pd.Series()
            ax.scatter(x=_df["feature_x"].map(_x_label_numeric),
                       y=_df["feature_y"].map(_y_label_numeric),
                       marker=shape, c=_df["corr"].apply(palette),
                       s=_df["size"], alpha=_df["alpha"])

            # Fixing labels on the x-axis, map from numeric to the actual feature name
            ax.set_xticks([_x_label_numeric[v] for v in _x_label])
            ax.set_xticklabels(_x_label, rotation=45, horizontalalignment="right", fontsize=label_size)

            # Fixing labels on the y-axis, map from numeric to the actual feature name
            ax.set_yticks([_y_label_numeric[v] for v in _y_label])
            ax.set_yticklabels(_y_label, fontsize=label_size)

            # Upper and lower padding
            _padding = 0.5
            ax.set_xlim([- _padding, max([v for v in _x_label_numeric.values()]) + _padding])
            ax.set_ylim([- _padding, max([v for v in _y_label_numeric.values()]) + _padding])

            # Remove spine
            for sp in ["top", "right", "bottom", "left"]:
                ax.spines[sp].set_visible(False)

        if not ax:
            return _df
