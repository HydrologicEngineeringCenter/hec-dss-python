# import pandas as pd
import numpy as np
import math

NULL_INT = -3.4028234663852886e+38

class GriddedData:
    """container for gridded (Raster) data

    Properties:
        id = dss pathname 
        type :  
                400:Undefined grid with time
                401:Undefined grig
                410:HRAP grid with time reference
                411:HRAP grid
                420:Albers with time reference
                421:Albers
                430:Specified Grid with time reference
                431:Specified Grid
        dataType : 
                PER_AVER = 0, 
                PER_CUM = 1,
                INST_VAL = 2, 
                INST_CUM = 3, 
                FREQ = 4, 
                INVALID = 5
        lowerLeftCellX = 0
        lowerLeftCellY = 0
        numberOfCellsX = 0
        numberOfCellsY = 0
        numberOfRanges = 0
        srsDefinitionType = 0
        timeZoneRawOffset = 0
        isInterval = 0
        isTimeStamped = 0
        dataUnits = ""
        dataSource = ""
        srsName = ""
        srsDefinition = ""
        timeZoneID = ""
        cellSize = 0.0
        xCoordOfGridCellZero = 0.0
        yCoordOfGridCellZero = 0.0
        nullValue = 0.0
        maxDataValue = 0.0
        minDataValue = 0.0
        meanDataValue = 0.0
        rangeLimitTable = []
        numberEqualOrExceedingRangeLimit = []
        data = np.zeros(0)

    """
    def __init__(self):
        self.id = None
        self.type = 0
        self.data_type = 0
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
        self.data = np.zeros(0)
        self.location_info = None

    def range_limit_table(self, minval, maxval, range_, bins, datasize, data):
        max_bins = 15

        if bins > max_bins:
            bins = max_bins

        self.rangeLimitTable = [0] * bins
        self.numberEqualOrExceedingRangeLimit = [0] * bins

        self.rangeLimitTable[0] = NULL_INT
        self.rangeLimitTable[1] = minval

        step = range_ / bins

        for i in range(2, bins):
            self.rangeLimitTable[i] = minval + step * i

        self.rangeLimitTable[bins - 1] = maxval

        # Exceedance
        for idx in range(datasize):
            for jdx in range(bins):
                if data[idx] >= self.rangeLimitTable[jdx]:
                    self.numberEqualOrExceedingRangeLimit[jdx] += 1

    def update_grid_info(self):
        self.numberOfCellsX = len(self.data[0])
        self.numberOfCellsY = len(self.data)
        n = np.size(self.data)
        self.maxDataValue = np.nanmax(self.data)
        self.minDataValue = np.nanmin(self.data)
        bin_range = int(math.ceil(self.maxDataValue) - math.floor(self.minDataValue))
        self.meanDataValue = np.nanmean(self.data)
        
        self.data = np.nan_to_num(self.data, nan=NULL_INT)
        self.numberOfRanges = math.floor(1 + 3.322 * math.log10(n) + 1)
        flat_data = self.data.flatten()
        self.range_limit_table(self.minDataValue, self.maxDataValue, bin_range, self.numberOfRanges, n, flat_data)

    @staticmethod
    def create(path=None,
        type = 420,
        dataType = 1,
        lowerLeftCellX = 0,
        lowerLeftCellY = 0,
        numberOfCellsX = 0,
        numberOfCellsY = 0,
        numberOfRanges = 0,
        srsDefinitionType = 0,
        timeZoneRawOffset = 0,
        isInterval = 0,
        isTimeStamped = 0,
        dataUnits = "MM",
        dataSource = "",
        srsName = "WKT",
        srsDefinition = 'PROJCS["USA_Contiguous_Albers_Equal_Area_Conic_USGS_version",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-96.0],PARAMETER["Standard_Parallel_1",29.5],PARAMETER["Standard_Parallel_2",45.5],PARAMETER["Latitude_Of_Origin",23.0],UNIT["Meter",1.0]]',
        timeZoneID = "",
        cellSize = 2000.0,
        xCoordOfGridCellZero = 0.0,
        yCoordOfGridCellZero = 0.0,
        nullValue = 0.0,
        maxDataValue = 0.0,
        minDataValue = 0.0,
        meanDataValue = 0.0,
        rangeLimitTable = [],
        numberEqualOrExceedingRangeLimit = [],
        data=np.zeros(0),
        location_info=None):

        gd = GriddedData()
        gd.id = path
        gd.type = type
        gd.data_type = dataType
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
        gd.data = np.array(data)
        gd.location_info = location_info

        gd.update_grid_info()

        return gd

