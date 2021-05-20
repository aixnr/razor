# Aizan's Collection of Razor Tools

Collection of small and reusable Python tools by Aizan.

## Importing this module

On Windows machine, it can be done as follows:

```python
import sys; sys.path.append(r"C:\Users\my_user\Documents\Repo\razor")
```

Assuming the repo exists at this location: `C:\Users\my_user\Documents\Repo\razor`, a.k.a `Documents\Repo\razor`.

## Tools

1. [Sigmoid curve fitter](#sigmoid-curve-fitter)
2. [Confidence interval](#confidence-interval)
3. [Avidity index calculator](#avidity-index-calculator)

## Sigmoid curve fitter

Provide `x_data` and `y_data` as lists, each value at index `n` corresponding to one another. Usually, `x_data` is the concentration or dilution of analyte, while `y_data` is the readout (e.g. OD values).

Quick tutorial:

```python
# Module import
from curvemod import Sigmoid

# Instantiate Sigmoid class
my_curve = Sigmoid(x=x_data, y=y_data)

# Plot the fitted curve
fig, ax = plt.subplots()
my_curve.curve(ax=ax, fit=my_curve.fit())

# Show r2 value as legend
my_curve.r2(fit=my_curve.fit(), ax=ax)
```

The `.fit()` method of this `Sigmoid` class outputs the 4 parameters from this sigmoidal 4PL logistic function.

If plotting multiple curves with data in a Pandas `DataFrame`, turn Pandas `Series` into list with `.to_list()` method, for example:

```python
_x = _df["Dilution"].to_list()
_y = _df["OD450"].to_list()
```

In the case where `four_pl()` computation would fail due to *ugly* y-values, there is `.spline()` method that would instead draw a B-spline smoothing for the data.

```python
# Assume the same my_curve Sigmoid object as above
my_curve.spline(ax=ax, color="tomato")
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
