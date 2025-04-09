from enum import Enum

class DssType(Enum):
    """
    Enum class representing different types of DSS (Data Storage System) types.

    Attributes:
        PER_AVER (str): Period average.
        PER_CUM (str): Period cumulative.
        INST_VAL (str): Instantaneous value.
        INST_CUM (str): Instantaneous cumulative.
        FREQ (str): Frequency (not a DSS standard yet).
        PER_MAX (str): Period maximum (not a DSS standard yet).
        PER_MIN (str): Period minimum (not a DSS standard yet).
        CONST (str): Constant (not a DSS standard yet).
    """
    PER_AVER = "PER-AVER"
    PER_CUM = "PER-CUM"
    INST_VAL = "INST-VAL"
    INST_CUM = "INST-CUM"
    # items below are not DSS standard (yet!)
    FREQ = "FREQ"
    PER_MAX = "PER-MAX"
    PER_MIN = "PER-MIN"
    CONST = "CONST"

    def __str__(self):
        """
        Returns the string representation of the enum value.

        Returns:
            str: The value of the enum member.
        """
        return self.value