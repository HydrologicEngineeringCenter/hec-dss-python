from enum import Enum


class DssType(Enum):
    PER_AVER = "PER-AVER"
    PER_CUM = "PER-CUM"
    INST_VAL = "INST-VAL"
    INST_CUM = "INST-CUM"
    FREQ = "FREQ"
    PER_MAX = "PER-MAX"
    PER_MIN = "PER-MIN"
    CONST = "CONST"

