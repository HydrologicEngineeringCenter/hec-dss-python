# import pandas as pd
import numpy as np
import math

NULL_INT = -3.4028234663852886e+38

class GriddedData:
    """
    Container for gridded (Raster) data.

    Properties:
        id (str): DSS pathname.
        type (int): Grid type.
            400: Undefined grid with time.
            401: Undefined grid.
            410: HRAP grid with time reference.
            411: HRAP grid.
            420: Albers with time reference.
            421: Albers.
            430: Specified Grid with time reference.
            431: Specified Grid.
        dataType (int): Data type.
            PER_AVER = 0.
            PER_CUM = 1.
            INST_VAL = 2.
            INST_CUM = 3.
            FREQ = 4.
            INVALID = 5.
        lowerLeftCellX (int): X coordinate of the lower left cell.
        lowerLeftCellY (int): Y coordinate of the lower left cell.
        numberOfCellsX (int): Number of cells in the X direction.
        numberOfCellsY (int): Number of cells in the Y direction.
        numberOfRanges (int): Number of ranges.
        srsDefinitionType (int): SRS definition type.
        timeZoneRawOffset (int): Time zone raw offset.
        isInterval (int): Interval flag.
        isTimeStamped (int): Timestamp flag.
        dataUnits (str): Data units.
        dataSource (str): Data source.
        srsName (str): SRS name.
        srsDefinition (str): SRS definition.
        timeZoneID (str): Time zone ID.
        cellSize (float): Cell size.
        xCoordOfGridCellZero (float): X coordinate of grid cell zero.
        yCoordOfGridCellZero (float): Y coordinate of grid cell zero.
        nullValue (float): Null value.
        maxDataValue (float): Maximum data value.
        minDataValue (float): Minimum data value.
        meanDataValue (float): Mean data value.
        rangeLimitTable (list): Range limit table.
        numberEqualOrExceedingRangeLimit (list): Number equal or exceeding range limit.
        data (numpy.ndarray): Data array.
    """

    def __init__(self):
        """
        Initialize a GriddedData object with default values.
        """
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
        """
        Calculate the range limit table and the number of values equal or exceeding each range limit.

        Args:
            minval (float): Minimum value.
            maxval (float): Maximum value.
            range_ (float): Range of values.
            bins (int): Number of bins.
            datasize (int): Size of the data.
            data (numpy.ndarray): Data array.
        """
        max_bins = 15

        if bins > max_bins:
            bins = max_bins

        self.rangeLimitTable = np.empty(bins, dtype=float)
        self.rangeLimitTable[0] = NULL_INT
        self.rangeLimitTable[1] = minval

        step = range_ / bins
        self.rangeLimitTable[2:] = minval + step * np.arange(2, bins)

        self.rangeLimitTable[bins - 1] = maxval
        # Exceedance
        mask = data[None, :] >= self.rangeLimitTable[:, None]
        self.numberEqualOrExceedingRangeLimit = mask.sum(axis=1)

    def update_grid_info(self):
        """
        Update grid information based on the data array.
        """
        self.numberOfCellsX = len(self.data[0])
        self.numberOfCellsY = len(self.data)
        n = np.size(self.data)
        self.maxDataValue = np.nanmax(self.data)
        self.minDataValue = np.nanmin(self.data)
        bin_range = int(math.ceil(self.maxDataValue) - math.floor(self.minDataValue))
        self.meanDataValue = np.nanmean(self.data)

        self.data = np.nan_to_num(self.data, nan=NULL_INT)
        self.numberOfRanges = math.floor(2 + 3.322 * math.log10(n))
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
        """
        Create a new GriddedData object with the specified parameters.

        Args:
            path (str, optional): DSS pathname. Defaults to None.
            type (int, optional): Grid type. Defaults to 420.
            dataType (int, optional): Data type. Defaults to 1.
            lowerLeftCellX (int, optional): X coordinate of the lower left cell. Defaults to 0.
            lowerLeftCellY (int, optional): Y coordinate of the lower left cell. Defaults to 0.
            numberOfCellsX (int, optional): Number of cells in the X direction. Defaults to 0.
            numberOfCellsY (int, optional): Number of cells in the Y direction. Defaults to 0.
            numberOfRanges (int, optional): Number of ranges. Defaults to 0.
            srsDefinitionType (int, optional): SRS definition type. Defaults to 0.
            timeZoneRawOffset (int, optional): Time zone raw offset. Defaults to 0.
            isInterval (int, optional): Interval flag. Defaults to 0.
            isTimeStamped (int, optional): Timestamp flag. Defaults to 0.
            dataUnits (str, optional): Data units. Defaults to "MM".
            dataSource (str, optional): Data source. Defaults to "".
            srsName (str, optional): SRS name. Defaults to "WKT".
            srsDefinition (str, optional): SRS definition. Defaults to a specific Albers projection.
            timeZoneID (str, optional): Time zone ID. Defaults to "".
            cellSize (float, optional): Cell size. Defaults to 2000.0.
            xCoordOfGridCellZero (float, optional): X coordinate of grid cell zero. Defaults to 0.0.
            yCoordOfGridCellZero (float, optional): Y coordinate of grid cell zero. Defaults to 0.0.
            nullValue (float, optional): Null value. Defaults to 0.0.
            maxDataValue (float, optional): Maximum data value. Defaults to 0.0.
            minDataValue (float, optional): Minimum data value. Defaults to 0.0.
            meanDataValue (float, optional): Mean data value. Defaults to 0.0.
            rangeLimitTable (list, optional): Range limit table. Defaults to [].
            numberEqualOrExceedingRangeLimit (list, optional): Number equal or exceeding range limit. Defaults to [].
            data (numpy.ndarray, optional): Data array. Defaults to np.zeros(0).
            location_info (LocationInfo, optional): Location info assotiated with record container.

        Returns:
            GriddedData: A new GriddedData object.
        """
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