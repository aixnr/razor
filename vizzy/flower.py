"""
Flow cytometry script collection
"""

# Import requires modules
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


class Comp:
    """
    """
    def __init__(self, csv):
        _csv = pd.read_csv(csv)

        # Melt into tidy (long) format, then fix values on the lower end
        _df = pd.melt(_csv, var_name="Channel", value_name="Fl")
        _df["Fl"] = np.where(_df["Fl"] < 10, 5, _df["Fl"])

        self.df = _df.copy()

    def grid(self, aspect=2.5, height=1.25):
        # Use transparent background
        sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})

        # Set up FacetGrid object (like GridSpec)
        g = sns.FacetGrid(self.df, row="Channel", aspect=aspect, height=height,
                          sharey=False, sharex=True)

        # Map each channel to show their fluorescence value
        g.map_dataframe(sns.kdeplot, x="Fl", log_scale=True, fill=True)

        # Default plot title for each grid is annoying, trim it down
        g.set_titles(row_template='{row_name}')

        # Turn off y-ticks
        g.set(yticks=[])


class Peak:
    """
    To investigate overall marker expression of gated population, use this Peak class

    1) Export the gated population as Scale Values on FlowJo
    2) Remove the un-needed columns (scatters and time)
    3) Then pass the cleaned-up DataFrame as df to this class
    4) Then, plot it!
    """
    def __init__(self, df, drop):
        """ __init__ class constructor
        """
        self._df = df.applymap(lambda x: 10 if x < 9.9 else x).applymap(np.log10)
        self._df = pd.melt(self._df, var_name="Stain", value_name="FI")

        # If drop keyword is supplied with values
        if drop:
            self._df = self._df.query("Stain != @drop")

    def plot(self, **kwargs):
        # Default keyword arguments
        kws = {"aspect": 4, "height": 1}

        # Over-writing the default keyword arguments
        for _key, _value in kwargs.items():
            if _key not in kws.keys():
                raise Exception(f"Error: Invalid kwargs '{_key}'. Accepted **kwargs are {[x for x in kws.keys()]}")
            if _key in kws.keys():
                kws[_key] = _value

        # Copy the DataFrame to make typing easier
        _df = self._df.copy()

        # Instantiate the FacetGrid object
        g = sns.FacetGrid(_df, row="Stain", aspect=kws["aspect"], height=kws["height"], sharey=False, sharex=True)

        # Draw the density, with white overlay
        g.map_dataframe(sns.kdeplot, "FI", bw_adjust=.5, clip_on=False, fill=True, alpha=1, lw=1.5)
        g.map_dataframe(sns.kdeplot, "FI", clip_on=False, color="w", lw=2, bw_adjust=.5)

        # Remove un-needed elements
        g.set_titles("")
        g.set(yticks=[], ylabel="", xlabel=r"Intensity (log$_{10}$-transformed)", xlim=(1, 5.5))
        g.despine(left=True)

        # Ugly way to print names prettily and adding x-axis grid
        # -------------------------------------------------------

        # Get the stain name without fluorochrome, hence the split
        _title = [x.split()[0] for x in _df["Stain"].unique().tolist()]

        # Index counter
        _i = 0

        # Start the looper
        for axlist in g.axes:
            for ax in axlist:
                # Adding the stain name
                # ax.text(0.75, .4, s=_title[_i], ha="left")  # using ax.text()
                ax.set_ylabel(f"{_title[_i]}")                # using ax.set_ylabel()
                _i += 1
                # Adding the x grid
                ax.grid(which="major", axis="x", alpha=0.5, color="gray")
