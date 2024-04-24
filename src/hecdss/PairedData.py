# import pandas as pd

class PairedData:
    def __init__(self):
        self.path = None
        self.ordinates = []
        self.values = []
        self.labels = []
        self.type_independent = ""
        self.type_dependent = ""
        self.units_independent = ""
        self.units_dependent = ""
        self.location_information = None

    def curve_count(self):
        return len(self.values)

    # def to_data_frame(self, include_index=False):
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
    def create(x_values, y_values, x_units="", x_type="", y_units="", y_type="", path=None):
        pd = PairedData()
        pd.path = path
        pd.ordinates = x_values
        pd.values = y_values
        pd.units_independent = x_units
        pd.units_dependent = y_units
        pd.type_independent = x_type
        pd.type_dependent = y_type
        return pd

