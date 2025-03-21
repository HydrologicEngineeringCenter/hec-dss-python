import re

from hecdss import DssPath, RegularTimeSeries
from hecdss.dss_type import DssType


class CwmsUtility:
    """
    These Utility methods are used to convert between CWMS and DSS conventions
    This is a short term solution.  Longer term we will be using the following library:
    https://github.com/HydrologicEngineeringCenter/hec-python-library

    """

    CWMS_DSS_INTERVAL_MAP = {
        "1Minute": "1Minute",
        "2Minutes": "2Minute",
        "3Minutes": "3Minute",
        "4Minutes": "4Minute",
        "5Minutes": "5Minute",
        "6Minutes": "6Minute",
        "12Minutes": "12Minute",
        "15Minutes": "15Minute",
        "20Minutes": "20Minute",
        "30Minutes": "30Minute",
        "1Hour": "1Hour",
        "2Hours": "2Hour",
        "3Hours": "3Hour",
        "4Hours": "4Hour",
        "6Hours": "6Hour",
        "8Hours": "8Hour",
        "12Hours": "12Hour",
        "1Day": "1Day",
        # # DSS doesn't support the 2Day, 3Day, etc...  intervals.
        # '2Days': '',
        # '3Days': '',
        # '4Days': '',
        # '5Days': '',
        # '6Days': '',
        "1Week": "1Week",
        "1Month": "1Month",
        "1Year": "1Year",
        "0": "Ir-Month",  # not optimized for some cases
    }

    # build another map from DSS to CWMS (use lower case for DSS key)
    DSS_CWMS_INTERVAL_MAP = {v.lower(): k for k, v in CWMS_DSS_INTERVAL_MAP.items()}
    DSS_CWMS_INTERVAL_MAP["ir-day"] = "0"
    # DSS_CWMS_INTERVAL_MAP["ir-month"] = "0" # already included
    DSS_CWMS_INTERVAL_MAP["ir-year"] = "0"
    DSS_CWMS_INTERVAL_MAP["ir-decade"] = "0"
    DSS_CWMS_INTERVAL_MAP["ir-century"] = "0"

    @staticmethod
    def get_cwms_parameter_type(dss_type: DssType):
        s = str(dss_type).upper()
        if "INST" in s:
            return "Inst"
        elif "AVE" in s:
            return "Ave"
        elif "CUM" in s:
            return "Total"
        elif "MAX" in s:
            return "Max"
        elif "MIN" in s:
            return "Min"
        elif "CONST" in s:
            return "Const"
        else:
            return "Inst"

    @staticmethod
    def pathname_to_cwms_tsid(path, dss_type="", duration="0", strict=False):
        """
        pathname is a dsspath name. Example: /TULA//Flow//1Hour/Ccp-Rev/
        type is

        returns CWMS convention time-series-id
        [Location]-[sub-location].[Parameter]-[sub-parameter].[Type].[Interval].[Duration].[Version]
        """
        p = DssPath(path, 0)
        a, b, c, e, f = p.A.strip(), p.B.strip(), p.C.strip(), p.E.strip(), p.F.strip()
        # drop a part (watershed by convention)
        # [Location]-[sub-location]
        tsid = b
        # [parameter]
        tsid += "." + c + "."
        # [Type]
        tsid += CwmsUtility.get_cwms_parameter_type(dss_type) + "."
        # [Interval]
        tsid += CwmsUtility._convert_dss_interval_to_cwms_interval(e) + "."
        # [Duration]
        tsid += duration + "."
        # [Version]
        tsid += f
        if strict:
            return tsid.title()
        return tsid

    @staticmethod
    def cwms_ts_id_to_dss_path(ts_id: str) -> DssPath:
        """
        convert cwms time-series id to a dss path
        example input:
        "NORK-Norton-Prairie_Dog.Stage.Inst.15Minutes.0.nwklrgs-raw"
        example output:
        "//NORK-Norton-Prairie_Dog/Stage/01Apr2024/15Minute/nwklrgs-raw/"

        """
        # Be sure there are no slashes used anywhere in the name
        ts_id = ts_id.replace("/", "-")
        # Replace period separators with slashes so we can split it
        ts_id = ts_id.replace(".", "/")
        location, parameter, cwms_type, cwms_interval, duration, version = ts_id.split(
            "/"
        )[:6]

        path = DssPath("///////", 0)
        path.A = ""
        path.B = location
        path.C = parameter
        path.D = ""
        path.E = CwmsUtility._convert_cwms_interval_to_dss_interval(cwms_interval)
        path.F = version

        return path.path_without_date()

    @staticmethod
    def _convert_cwms_interval_to_dss_interval(cwms_interval: str):
        """
        Converts CWMS interval to DSS interval
        for example   '2Minutes' is converted to '2Minute'
        """

        if cwms_interval in CwmsUtility.CWMS_DSS_INTERVAL_MAP:
            return CwmsUtility.CWMS_DSS_INTERVAL_MAP[cwms_interval]

        if len(cwms_interval) > 1 and cwms_interval[0] == "~":  # pseudo regular
            if cwms_interval[1:] in CwmsUtility.CWMS_DSS_INTERVAL_MAP:
                return "~" + CwmsUtility.CWMS_DSS_INTERVAL_MAP[cwms_interval[1:]]

        raise ValueError(
            f"The cwms interval '{cwms_interval}' is invalid, or there is not a supported conversion to DSS"
        )

    @staticmethod
    def _convert_dss_interval_to_cwms_interval(dss_interval: str):
        """
        Converts dss interval to CWMS interval
        for example   '12Hour' is converted to '12Hours'
        """
        e_part = dss_interval.lower()
        if e_part in CwmsUtility.DSS_CWMS_INTERVAL_MAP:
            return CwmsUtility.DSS_CWMS_INTERVAL_MAP[e_part]

        if len(e_part) > 1 and e_part[0] == "~":
            if e_part[1:] in CwmsUtility.DSS_CWMS_INTERVAL_MAP:
                return "~" + CwmsUtility.DSS_CWMS_INTERVAL_MAP[e_part[1:]]

        raise ValueError(
            f"The dss interval '{dss_interval}' is invalid, or there is not a supported conversion to a "
            f"CWMS interval"
        )

    @staticmethod
    def dss_data_type_from_cwms_tsid(cwms_tsid) -> str:
        """
        takes an input id such as 'TULA.Flow.Inst.1Hour.0.Ccp-Rev'
        and returns the DSS DataType  'INST-VAL' in this example
        :param cwms_tsid: input time-series identifier
        :return: string representing a dss data type
        """
        parts = cwms_tsid.split(".")
        parameter = parts[1]
        ts_type = parts[2]
        if ts_type == "Inst":
            if parameter == "Precip":
                dss_type = DssType.INST_CUM
            else:
                dss_type = DssType.INST_VAL
        elif ts_type == "Total":
            dss_type = DssType.PER_CUM
        elif ts_type == "Ave":
            dss_type = DssType.PER_AVER
        elif ts_type == "Max":
            dss_type = DssType.PER_MAX
        elif ts_type == "Min":
            dss_type = DssType.PER_MIN
        else:
            dss_type = ts_type  # default: use cwms type
        return str(dss_type)

    @staticmethod
    def cwms_to_regular_timeseries(data):
        """
        Convert a CWMS (pandas-dataframe) TimeSeries to a RegularTimeSeries
        """
        times = data.df["date-time"].to_list()
        values = data.df["value"].to_list()
        cwms_tsid = data.json["name"]
        data_type = CwmsUtility.dss_data_type_from_cwms_tsid(cwms_tsid)
        units = data.json["units"]
        dss_path = CwmsUtility.cwms_ts_id_to_dss_path(cwms_tsid)

        if dss_path.E[:2].lower() == "ir":
            raise ValueError(
                f"Irregular time series not implemented in cwms_to_timeseries method input: {cwms_tsid}"
            )

        ts = RegularTimeSeries.create(
            values,
            times,
            units=units,
            dataType=str(data_type),
            interval=dss_path.E,
            path=str(dss_path),
        )
        ts.id = str(dss_path)
        return ts

    @staticmethod
    def regular_time_series_to_json(rts: RegularTimeSeries, office_id: str, ts_id: str):
        """
        converts a regular timeseries into a JSON format that is
        compatible with the CWMS data API
        """
        # hard code flag = 0
        flag = 0
        # dss quality code is the same cwms
        values = [[d, v, flag] for d, v in zip(rts.times, rts.values)]

        json_result = {
            "name": ts_id,
            "office-id": office_id,
            "units": rts.units,
            "values": values,
            "version-date": None,
        }

        return json_result
