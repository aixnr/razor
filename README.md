# Razor Tools

Collection of small and reusable Python tools and utility scripts for plotting.

## Installation

This package is hosted only on GitHub and `git`-installable.

```bash
pip install git+https://github.com/aixnr/razor
```

The packages `curvemod` and `vizzy` are now available after installation.

## Tools

1. [Sigmoid curve fitter](#sigmoid-curve-fitter) with `curvemod.Sigmoid`
2. [Confidence interval](#confidence-interval) with `curvemod.ConfInt`
3. [Avidity index calculator](#avidity-index-calculator) with `curvemod.Avipy`
4. [Correlation heatmap](#correlation-heatmap) with `vizzy.Heatermap`
5. [LOWESS curve](#lowess-curve) with `curvemod.Lowess`
6. [Compensation Grid](#compensation-grid) with `vizzy.Comp` (in `flower.py`)

## Sigmoid curve fitter

Provide `x_data` and `y_data` as lists, each value at index `n` corresponding to one another. Usually, `x_data` is the concentration or dilution of analyte, while `y_data` is the readout (e.g. OD values).

Quick tutorial:

```python
# Module import
from curvemod import Sigmoid

fourpl = Sigmoid(x, y).fit()
fourpl.curve(ax=ax)
fourpl.r2(ax=ax)
fourpl.mid(ax=ax)
```

If plotting multiple curves with data in a Pandas `DataFrame`, turn Pandas `Series` into list with `.to_list()` method, for example:

```python
_x = _df["Dilution"].to_list()
_y = _df["OD450"].to_list()
```

## Confidence interval

Seaborn has `sns.regplot()` for plotting linear regression with minimal user input. However, it lacks customization, e.g. coloring each individual data points. The class `ConfInt` from the `curvemod` module can be used to draw linear regression line with `ConfInt.lin_reg()` method and the confidence interval band with `ConfInt.confidence_interval()` method.

Quick tutorial:

```python
# Import
from curvemod import ConfInt

# Load x and y value (list)
my_regression = ConfInt(x_data, y_data)

# Run the chart for both .confidence_interval() and .lin_reg()
fig, ax = plt.subplots()
my_regression.confidence_interval(ax=ax)
my_regression.lin_reg(ax=ax)
```

## Avidity index calculator

This module performs avidity index calculation, which is defined as the ratio of area under the curve (AUC) of antibody titration of the chaotrope-treated sample over the non-treated control sample. Basically:

```bash
avidity index = AUC of treated sample / AUC of non-treated control sample
```

This module will perform linear regression with `sklearn.linear_model.LinearRegression()` class, then it will return the predicted `y` value. This predicted `y` value will be used to calculate the avidity index. This works based on the assumption that the original `y` values present as a straight line on the log-transformed x-axis, and the predicted `y` value is used to increase the robustness of the analysis.

This module assumes the following columns are present:

* Subject
* Timepoint
* Isotype (e.g. IgG, IgA)
* Antigen
* Treated (Yes or No, as string)
* Blank (blank values for the negative control wells)
* dil_1, dil_2, dil_4, dil_8, dil_16, and dil_32, which hold the OD values

When `dilution_mapper` is not passed, it will use the default dilution scheme (1, 2, 4, 8, 16, and 32). Whenever the `dilution_mapper` is supplied (a dictionary, see example code below), it will re-map all the column names for the dilution series accordingly. This is *somewhat* important when it comes to calculating the AUC with `np.trapz()` function.

```python
# Module import
from curvemod import Avipy

# Load data from, presumably, a well-annotated Excel spreadsheet
df = pd.read_excel("spreadsheet")

# Provide dilution as dictionary to map the default values
dilution_mapper = {"dil_1": 200, 
                   "dil_2": 400, 
                   "dil_4": 800, 
                   "dil_8": 1600, 
                   "dil_16": 3200, 
                   "dil_32": 6400}

# Instantiate the Avipy object with the name avi
avi = Avipy(df, dilution_mapper=dilution_mapper)

# Return data the supplied data
avi.df()

# Calculate AUC
avi.auc()

# Calculate avidity index
avi.avidity_index()

# Plot the data
fig, ax = plt.subplots()
avi.plotter(subject, antigen, timepoint, isotype, ax, treshold=0.85)
```

The `.plotter()` method plots AUC from the predicted `y` values as line and shades the AUC till `y=0`, and it also plots the original `y` values with circular markers. It outputs, as legend, the R^2 (coefficient of determination) for treated and untreated samples, along with the avidity index. Use your judgment to validate a sample based on the R^2 value. If the R^2 is low (e.g. below 0.7), which indicates a weak agreement between the original and predicted y values, consider investigating that particular sample.

Special handlings:

* If negative value is encountered in predicted `y` value, `.auc()` method would change that into `0`. This would prevent from the AUC from being negative.
* If threshold is set, if the R^2 is below this value, the `marker` for the original data is set to triangle `^` instead of circle `o`.

## Correlation heatmap

The usual method to generate a correlation heatmap is by using the `.corr()` method on a Pandas DataFrame, and then draw a heatmap by feeding the output into `sns.heatmap()` (from Seaborn). This is already great, especially with the ability to use masking (see this tutorial on Towards Data Science: [Heatmap Basics with Seaborn](https://towardsdatascience.com/heatmap-basics-with-pythons-seaborn-fb92ea280a6c)) to create a triangular heatmap. 

After reading this post on Towards Data Science ([Better Heatmaps and Correlation Matrix Plots in Python](https://towardsdatascience.com/better-heatmaps-and-correlation-matrix-plots-in-python-41445d0f2bec)), I realized that heatmap is essentially a scatterplot. This led to the birth of this `Heatermap` class. Essentially, it encodes 2 information: the correlation (with marker's color for direction and size for strength) and the p-value (with marker's opacity). Strong correlation makes marker to have color that is intense (positive: red, negative: blue) while weaker correlation (below 0.5 in either direction) reduces the size of the marker. When the correlation isn't significant (p-value > 0.05), the marker turns dim.

Assume that a dataset has rows as observations and *n* columns as (unique) features with values being numeric (integer or float), then

```python
# Import pyplot and pandas
import matplotlib.pyplot as plt
import pandas as pd

# Import the Heatermap class and the colorbar() function
from vizzy import Heatermap
from vizzy.heatermap import colorbar

# Load data
df = pd.read_excel("spreadsheet.xlsx")

# Gridspec call, ax1 for the heatmap, ax2 for the colorbar
fig = plt.figure()
gs = fig.add_gridspec(1, 16)       # 16-column gridspec

# Main heatmap
ax1 = fig.add_subplot(gs[:, :-2])  # Column 1 -- 14
Heatermap(df).plotter(size_scale=1200, method="spearman", ax=ax1, shape="o")

# The colorbar
ax2 = fig.add_subplot(gs[:,-1])    # Column 16
colorbar(ax2, scale_spacing=5)
```

Explanation

* `Heatermap.plotter()` requires the `size_scale` to scale the marker, default is `500`. 
* It also accepts `feature_order` parameter to customize the positioning of labels on the x- and y-axis, overriding the automatic sorting. This `feature_order` can also be used to exclude columns that are present in the dataframe during plotting.
* Currently, `spearman` and `pearson` (default) methods are supported for calculating the R value.
* The `shape` paramater is passed to the `marker` parameter, where `s` is square, `o` is circle, etc. Refer to Matplotlib documentation for list of available shapes.
* For `colorbar()` function, `scale_spacing` refers to the number of y-tick spacings.

As an additional note regarding to cleaning data, consider performing log-transformation (i.e. transform data into log2 or log10-based) prior to using parametric statistical test. Check the values afterwards with Shapiro-Wilk test or run a Q-Q plot so see the *normality* of the data.

Special handling: dealing with outliers using robust scaling and winsorization. Sometimes, the data could have outliers that could nudge the p-value towards significance and strong R value in either direction. To deal with this annoying situation, scaling the values and performing winsorization might help. The code block below taken from my A-039 analysis on human IgG multiplex data.

```python
from scipy.stats.mstats import winsorize
from sklearn.preprocessing import RobustScaler

def robust_scaling(data, drop_col=["Type", "Day"]):
    _scaler = RobustScaler()
    _df = data.drop(columns=drop_col).reset_index(drop=True)
    _columns_antigen = _df.columns[1:]
    
    # Winsorize 10% highest and lowest value
    for ag in _columns_antigen:
        _df[ag] = [x for x in winsorize(_df[ag].to_list(), limits=[0.1, 0.1]).data]
    
    # Re-scale
    for ag in _columns_antigen:
        _df[ag] = _scaler.fit_transform(_df[[ag]])
    return _df
```

## LOWESS Curve

```python
# Import matplotlib.pyplot
import matplotlib.pyplot as plt

# Import the class
from curvemod import Lowess

# Import function to generate example data
from curvemod.lowess import data_example

# Example
x, y = data_example()
lowess = Lowess(x, y)

fig, ax = plt.subplots()

lowess.plot(ax=ax)
lowess.fit(ax=ax)
lowess.conf_int(ax=ax, band="percentile", **kwargs)
```

For the `lowess.conf_int()` method, it accepts the following keyword arguments:

- `color`, for setting the color of the band; default to `steelblue`.
- `alpha`, for setting the transparency of the band; default to 0.1.
- `interval`, for setting the confidence interval; default to 95 for 95%.

## Compensation Grid

```python
from vizzy import Comp

Comp("/path/to/exporter_fsc.csv").grid()
```
