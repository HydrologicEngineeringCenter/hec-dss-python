# import pandas as pd
import numpy as np


class PairedData:
    def __init__(self):
        """
        Initialize a PairedData object with default values.
        """
        self.id = None
        self.ordinates = np.empty(0)
        self.values = np.empty(0)
        self.labels = []
        self.type_independent = ""
        self.type_dependent = ""
        self.units_independent = ""
        self.units_dependent = ""
        self.time_zone_name = ""
        self.location_info = None

    def curve_count(self):
        """
        Retrieve the number of curves in the paired data.

        Returns:
        int: The number of curves.
        """
        return len(self.values)

    # def to_data_frame(self, include_index=False):
    #     """
    #     Convert the paired data to a pandas DataFrame.
    #
    #     Parameters:
    #     include_index (bool, optional): Whether to include an index column. Defaults to False.
    #
    #     Returns:
    #     pandas.DataFrame: The paired data as a DataFrame.
    #     """
    #     data = {"stage": self.ordinates}
    #     for i in range(len(self.values)):
    #         label = self.labels[i] if i < len(self.labels) else f"value{i + 1}"
    #         data[label] = self.values[i]
    #
    #     if include_index:
    #         data["index"] = list(range(1, len(self.ordinates) + 1))
    #
    #     return pd.DataFrame(data)

    @staticmethod
    def create(x_values, y_values, labels=[], x_units="", x_type="", y_units="", y_type="", time_zone_name="", path=None):
        """
        Create a PairedData object with the provided data.

        Parameters:
        x_values (list of float): The independent variable values.
        y_values (list of list of float): The dependent variable values.
        labels (list of str, optional): The labels for the dependent variables. Defaults to an empty list.
        x_units (str, optional): The units of the independent variable. Defaults to an empty string.
        x_type (str, optional): The type of the independent variable. Defaults to an empty string.
        y_units (str, optional): The units of the dependent variable. Defaults to an empty string.
        y_type (str, optional): The type of the dependent variable. Defaults to an empty string.
        path (str, optional): The path identifier for the paired data. Defaults to None.

        Returns:
        PairedData: An instance of the PairedData class.
        """
        pd = PairedData()
        pd.id = path
        pd.ordinates = np.array(x_values)
        pd.values = np.array(y_values)
        pd.labels = labels
        pd.units_independent = x_units
        pd.units_dependent = y_units
        pd.type_independent = x_type
        pd.type_dependent = y_type
        pd.time_zone_name = time_zone_name
        return pd