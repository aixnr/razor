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

## Confidence interval

Seaborn has `sns.regplot()` for plotting linear regression with minimal user input. However, it lacks customization, e.g. coloring each individual data points. The class `ConfInt` from the `curvemod` module can be used to draw linear regression line with `ConfInt.lin_reg()` method and the confidence interval band with `ConfInt.confidence_interval()` method.

Quick tutorial:

```python
my_regression = ConfInt(x_data, y_data)

fig, ax = plt.subplots()
my_regression.confidence_interval(ax=ax)
my_regression.lin_reg(ax=ax)
```
