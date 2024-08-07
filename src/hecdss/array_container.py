import numpy as np
from typing import List


class ArrayContainer:

    def __init__(self):
        self.id = None
        self.values = None

    @staticmethod
    def create_int_array(values: List[int], path=None):
        a = ArrayContainer()
        a.id = path
        a.values = np.array(values, dtype=np.int)
        return a

    @staticmethod
    def create_float_array(values: List[float], path=None):
        a = ArrayContainer()
        a.id = path
        a.values = np.array(values, dtype=np.float32)
        return a

    @staticmethod
    def create_double_array(values: List[float], path=None):
        a = ArrayContainer()
        a.id = path
        a.values = np.array(values, dtype=np.float64)
        return a

    def __str__(self):
        if self.id is not None:
            identifier = f"id: {self.id}, "
        else:
            identifier = ""
        return f"{identifier}type: {self.values.dtype}, shape: {self.values.shape}, values: {self.values.tolist()}"