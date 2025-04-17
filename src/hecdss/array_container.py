import numpy as np
from typing import List


class ArrayContainer:

    def __init__(self):
        self.id = None
        self.int_values = None
        self.float_values = None
        self.double_values = None
        self.location_info = None

    @staticmethod
    def create_array_container(int_values: List[int] = [], float_values: List[float] = [],
                               double_values: List[float] = [], path=None, location_info=None):
        a = ArrayContainer()
        a.id = path
        a.int_values = np.array(int_values, dtype=np.int32)
        a.float_values = np.array(float_values, dtype=np.float32)
        a.double_values = np.array(double_values, dtype=np.float64)
        a.location_info = location_info
        return a

    def __str__(self):
        if self.id is not None:
            identifier = f"id: {self.id}, "
        else:
            identifier = ""
        return f"{identifier}\ntype: {self.int_values.dtype}, shape: {self.int_values.shape}, values: {self.int_values.tolist()}" \
               f"\ntype: {self.float_values.dtype}, shape: {self.float_values.shape}, values: {self.float_values.tolist()}" \
               f"\ntype: {self.double_values.dtype}, shape: {self.double_values.shape}, values: {self.double_values.tolist()}"
