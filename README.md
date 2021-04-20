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
```

## Confidence interval

Something here
