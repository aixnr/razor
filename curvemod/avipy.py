# --------------------------------------------------------------- #
# Aizan's Avipy class for automated avidity index calculation     #
# The important part of this script is the LinearRegression class #
# --------------------------------------------------------------- #

import numpy as np
from sklearn.linear_model import LinearRegression
from matplotlib.ticker import ScalarFormatter


class Avipy:
    def __init__(self, data, dilution_mapper=None):
        # Read data
        self.data = data.copy()

        # Working with dilution mapping
        if not dilution_mapper:
            default_dilution = {"dil_1": 1, "dil_2": 2, "dil_4": 4, "dil_8": 8, "dil_16": 16, "dil_32": 32}
            self.data = self.data.rename(columns=default_dilution)
            self.dilution = [value for key, value in default_dilution.items()]
        if dilution_mapper:
            self.data = self.data.rename(columns=dilution_mapper)
            self.dilution = [value for key, value in dilution_mapper.items()]

        # Applying blank to OD values, the .apply()
        for _col in self.dilution:
            self.data[_col] = self.data.apply(lambda x: x[_col] - x["Blank"], axis=1)

        # Remove blank column
        self.data = self.data.drop(columns="Blank")

    def df(self):
        """Return the data table stored in the object
        """
        return self.data

    def fit(self):
        """Return fitted data

        This will create an additional column for the R^2 and also
          6 additional columns of the fitted value
            Those columns are "dilution_n, pred" for the predicted y from the linear model.

        The np.reshape(-1, 1) is called on the X because X is required to be a 2-dimensional np.array()
        Then, X is log2-transformed
        """
        # Shared variables within this function
        values_X_log2 = np.log2(np.array(self.dilution).reshape(-1, 1))

        # Measuring the R^2, the function
        def _model(x, fit_type, _dilution=None):
            """Calculate the R^2 score using LinearRegression().fit(X, y) from sklearn

            X is log2-transformed with np.log2(), using values_X_log2 variable above.
            y is entered as is.
            """
            values_y = np.array(x[self.dilution])
            model = LinearRegression().fit(X=values_X_log2, y=values_y)

            if fit_type == "r2":
                return model.score(X=values_X_log2, y=values_y)
            elif fit_type == "pred":
                X = np.array(np.log2(_dilution)).reshape(-1, 1)
                return float(model.predict(X))
            else:
                raise Exception("Only accepts r2 or pred for the fit_type parameter")

        # Measuring the R^2 with .apply()
        self.data["R^2"] = self.data.apply(_model, args=('r2',), axis=1)

        # Return predicted y_values for each dilution
        for _dilution in self.dilution:
            self.data[f"{_dilution}, pred"] = self.data.apply(_model, args=("pred", _dilution), axis=1)

        # Return data
        return self.data

    def auc(self):
        """Calculate area under the curve (AUC)
        for the predicted values from the fitted linear regression model

        This function would drop the original y (OD) data,
          only showing the predicted y data.

        For AUC calculation, area cannot be a negative number. However, this method
          does not have a special handling for that.
          Predicted values < 0 would result in negative AUC. Change them to 0.

        TODO: Add a switch for AUC calculation using the actual data instead of fitted model
        """
        _df = self.fit()
        _df = _df.drop(columns=self.dilution)

        # Constant for column names of predicted values
        _columns = [f"{dilution}, pred" for dilution in self.dilution]

        # Change negative predicted value to 0 with .apply() and ternary operation
        for _col in _columns:
            _df[_col] = _df[_col].apply(lambda x: 0 if x < 0 else x)

        # Measuring the AUC, the function
        def _calculate_auc(x):
            """Calculating AUC using the np.trapz(y, x)
            """
            values_y = x[_columns]
            values_x = np.array(self.dilution)

            return np.trapz(y=values_y, x=values_x)

        # Measuring the AUC .apply()
        _df["AUC"] = _df.apply(_calculate_auc, axis=1)

        return _df

    def avidity_index(self):
        """Calculate the avidity index based on the AUC data from .auc() method

        I consider this function a little brittle, due to how it
          calculates the avidity index.
        """
        # Perform AUC calculation using the .auc() method
        _df = self.auc()

        # Find observation with AUC value of 0 under untreated to exclude from calculation
        # Because dividing a number by 0 results in a weird mathematical realm
        _zero_untreated = _df.query(" Treated == 'No' & AUC == 0 ")['Subject'].to_list()
        _df = _df.query(f" Subject != {_zero_untreated} ")

        # Drop the predicted y columns
        _columns_pred = [f"{dilution}, pred" for dilution in self.dilution]
        _df = _df.drop(columns=_columns_pred)

        # Great un-treated controls as a list
        _untreated = _df.query(" Treated == 'No' ")["AUC"].to_list()
        _treated = _df.query(" Treated == 'Yes' ")["AUC"].to_list()

        # Calculate the ratio of _treated over _untreated to get the index
        _avidity_index = []
        for _i, _element in enumerate(_untreated):
            _index = _treated[_i] / _untreated[_i]
            _avidity_index.append(_index)

        # Prepare the avidity index DataFrame (with a simple query filter) and return it
        _avidity_df = _df.query(" Treated == 'No' ").drop(columns=["AUC", "R^2", "Treated"]).reset_index(drop=True)
        _avidity_df["Avidity index"] = _avidity_index

        return _avidity_df

    def plotter(self, subject, antigen, timepoint=None, isotype="IgG", ax=None, threshold=0.85):
        """Plotter function to visualize the AUC

        Plots straight line for the predicted y
        Plots circular marker for the original y value

        Shades AUC with blue for the untreated (control).
        Shares AUC with red for the treated.

        Param
          subject   : Refer to original dataset
          antigen   : Refer to original dataset
          timepoint : Refer to original dataset
          isotype   : Refer to original dataset
          ax        : Axes object
          threshold : float; Below this value, change the marker from "o" to "^"
        """
        _x_original = self.dilution
        _x_predicted = [f"{dilution}, pred" for dilution in self.dilution]

        # Access avidity index
        _avidity_index = self.avidity_index().query("""
             Subject == @subject and \
             Isotype == @isotype and \
             Antigen == @antigen and \
             Timepoint == @timepoint
        """)["Avidity index"].to_list()[0]

        _df = self.fit().query("""
            Subject == @subject and \
            Isotype == @isotype and \
            Antigen == @antigen and \
            Timepoint == @timepoint
        """)

        # Set constants
        _color_untrt = "royalblue"
        _color_trt = "tomato"

        # Get y values for untreated controls
        _y_original_untrt = _df.query(" Treated == 'No' ").iloc[0][_x_original].to_list()
        _y_predicted_untrt = _df.query(" Treated == 'No' ").iloc[0][_x_predicted].to_list()

        # Get y values for treated
        _y_original_trt = _df.query(" Treated == 'Yes' ").iloc[0][_x_original].to_list()
        _y_predicted_trt = _df.query(" Treated == 'Yes' ").iloc[0][_x_predicted].to_list()

        # Access the R^2 values, then round to 3 decimal points
        _r2_untrt = round(_df.query(" Treated == 'No' ")["R^2"].to_list()[0], 3)
        _r2_trt = round(_df.query(" Treated == 'Yes' ")["R^2"].to_list()[0], 3)

        # Shape of the marker when R^2 reaches certain threshold
        _marker_original = {"untrt": "o", "trt": "o"}
        for _r, _k in zip([_r2_untrt, _r2_trt], ["untrt", "trt"]):
            if _r <= threshold:
                _marker_original[_k] = "^"
            elif _r > threshold:
                _marker_original[_k] = "o"

        # If Axes object not provided, return subsetted DataFrame
        if not ax:
            return _df

        # Begin plotting when Axes object is provided
        if ax:
            # Fill between for the area under the curve
            ax.fill_between(x=_x_original, y1=_y_predicted_untrt, y2=0, color=_color_untrt, alpha=0.08)
            ax.fill_between(x=_x_original, y1=_y_predicted_trt, y2=0, color=_color_trt, alpha=0.08)

            # Plot straight line from the predicted values
            ax.plot(_x_original, _y_predicted_untrt, color=_color_untrt)
            ax.plot(_x_original, _y_predicted_trt, color=_color_trt)

            # Plot circular markers for the original values
            ax.plot(_x_original, _y_original_untrt, color=_color_untrt, marker=_marker_original["untrt"], linestyle="")
            ax.plot(_x_original, _y_original_trt, color=_color_trt, marker=_marker_original["trt"], linestyle="")

            # Add legend for the R^2 values
            ax.plot([], [], label=f"AI: {round(_avidity_index, 3)}", linestyle="")
            ax.plot([], [], marker=_marker_original["untrt"], label=fr"R$^{2}$ untrt: {_r2_untrt}", color=_color_untrt)
            ax.plot([], [], marker=_marker_original["trt"], label=fr"R$^{2}$ trt: {_r2_trt}", color=_color_trt)
            ax.legend(frameon=False)

            # Customization
            ax.set_ylim(0, 3)
            ax.set_xscale("log", base=2)
            ax.xaxis.set_major_formatter(ScalarFormatter(useOffset=False))
            ax.ticklabel_format(style="plain", axis="x")
            ax.set_xticks(_x_original)

            if not timepoint:
                ax.set_title(f"{subject}, {isotype}, {antigen}")
            elif timepoint:
                ax.set_title(f"{subject} {timepoint}, {isotype}, {antigen}", loc="left")

            for _sp in ["top", "right"]:
                ax.spines[_sp].set_visible(False)
