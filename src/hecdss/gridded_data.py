# import pandas as pd

class GriddedData:
    def __init__(self):
        self.id = None
        self.type = 0
        self.dataType = 0
        self.lowerLeftCellX = 0
        self.lowerLeftCellY = 0
        self.numberOfCellsX = 0
        self.numberOfCellsY = 0
        self.numberOfRanges = 0
        self.srsDefinitionType = 0
        self.timeZoneRawOffset = 0
        self.isInterval = 0
        self.isTimeStamped = 0
        self.dataUnits = ""
        self.dataSource = ""
        self.srsName = ""
        self.srsDefinition = ""
        self.timeZoneID = ""
        self.cellSize = 0.0
        self.xCoordOfGridCellZero = 0.0
        self.yCoordOfGridCellZero = 0.0
        self.nullValue = 0.0
        self.maxDataValue = 0.0
        self.minDataValue = 0.0
        self.meanDataValue = 0.0
        self.rangeLimitTable = []
        self.numberEqualOrExceedingRangeLimit = []
        self.data = [[]]

    # def curve_count(self):
    #     return len(self.values)

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
    def create(path=None,
        type = 420,
        dataType = 0,
        lowerLeftCellX = 0,
        lowerLeftCellY = 0,
        numberOfCellsX = 0,
        numberOfCellsY = 0,
        numberOfRanges = 0,
        srsDefinitionType = 0,
        timeZoneRawOffset = 0,
        isInterval = 0,
        isTimeStamped = 0,
        dataUnits = "",
        dataSource = "",
        srsName = "",
        srsDefinition = "",
        timeZoneID = "",
        cellSize = 0.0,
        xCoordOfGridCellZero = 0.0,
        yCoordOfGridCellZero = 0.0,
        nullValue = 0.0,
        maxDataValue = 0.0,
        minDataValue = 0.0,
        meanDataValue = 0.0,
        rangeLimitTable = [],
        numberEqualOrExceedingRangeLimit = [],
        data=[[]]):

        gd = GriddedData()
        gd.id = path
        gd.type = type
        gd.dataType = dataType
        gd.lowerLeftCellX = lowerLeftCellX
        gd.lowerLeftCellY = lowerLeftCellY
        gd.numberOfCellsX = numberOfCellsX
        gd.numberOfCellsY = numberOfCellsY
        gd.numberOfRanges = numberOfRanges
        gd.srsDefinitionType = srsDefinitionType
        gd.timeZoneRawOffset = timeZoneRawOffset
        gd.isInterval = isInterval
        gd.isTimeStamped = isTimeStamped
        gd.dataUnits = dataUnits
        gd.dataSource = dataSource
        gd.srsName = srsName
        gd.srsDefinition = srsDefinition
        gd.timeZoneID = timeZoneID
        gd.cellSize = cellSize
        gd.xCoordOfGridCellZero = xCoordOfGridCellZero
        gd.yCoordOfGridCellZero = yCoordOfGridCellZero
        gd.nullValue = nullValue
        gd.maxDataValue = maxDataValue
        gd.minDataValue = minDataValue
        gd.meanDataValue = meanDataValue
        gd.rangeLimitTable = rangeLimitTable
        gd.numberEqualOrExceedingRangeLimit = numberEqualOrExceedingRangeLimit
        gd.data = data

        return gd

