from hecdss import DssPath
from hecdss.dss_type import DssType


class CwmsUtility:

    @staticmethod
    def get_cwms_parameter_type(dss_type):
        s = dss_type.upper()
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
    def pathname_to_cwms_tsid(path, dss_type=""):
        """
        pathname is a dsspath name. Example: /TULA//Flow//1Hour/Ccp-Rev/
        type is

        returns CWMS convention time-series-id
        [Location]-[sub-location].[Parameter]-[sub-parameter].[Type].[Interval].[Duration].[Version]
        """
        id_str = ""
        loc = ""
        p = DssPath(path, 0)
        a, b, c, e, f = p.A.strip(), p.B.strip(), p.C.strip(), p.E.string(), p.F.strip()
        if a != "":
            loc += a.capitalize()[:24]  # limit base location to 24 characters
        if b != "":
            loc += "-" + b.capitalize()[:32]  # limit sub-location to 32 characters

        loc += "." + c.capitalize() + "." + get_cwms_parameter_type(dss_type) + "."
        DateConverter.intervalString_to_sec(e)  # dss7 regular only. TODO: interval factor.
        # default_interval = IntervalFactory.find_any(
        #     IntervalFactory.equals_minutes(HecTimeSeries.get_interval_from_e_part(path.e_part()))) \
        #     .or_else(IntervalFactory.irregular())
        #
        # interval = IntervalFactory.find_any(equals_name(path.e_part())) \
        #     .or_else(default_interval) \
        #     .get_interval()

        # id_str += interval + "."
        #
        # if dss_type.upper().startswith("INS"):
        #     id_str += "0."
        # else:
        #     id_str += interval.replace(mil.army.usace.hec.metadata.Interval.LOCAL_AND_PSEUDOREGULAR_PREFIX,
        #                                "") + "."
        #
        # id_str += make_nice(path.f_part())
        # return id_str
        return loc

    @staticmethod
    def cwms_ts_id_to_pathname(ts_id: str) -> str:
        """
        convert cwms time-series id to a dss path
        example input:
        "NORK-Norton-Prairie_Dog.Stage.Inst.15Minutes.0.nwklrgs-raw"
        example output:
        "//NORK-Norton-Prairie_Dog/Stage/01Apr2024/15Minute/nwklrgs-raw/"

        """
        # Be sure there are no slashes used anywhere in the name
        ts_id = ts_id.replace('/', '-')
        # Replace period separators with slashes so we can split it
        ts_id = ts_id.replace('.', '/')
        location, parameter, cmws_type, cwms_interval, duration, version = ts_id.split('/')[:6]

        path = DssPath()
        path.A = ""
        path.B = location
        path.C = parameter
        path.D = ""
        path.E = cwms_interval
        path.F = version

        if cwms_interval == "0":
            path.E = "IR-MONTH"  # could be optimized (IR-DAY is better in some cases)

        return path.path_without_date()

    @staticmethod
    def dss_data_type_from_cwms_tsid(cwms_tsid):
        """
        takes an input id such as 'TULA.Flow.Inst.1Hour.0.Ccp-Rev'
        and returns the DSS DataType  'INST-VAL' in this example
        :param cwms_tsid: input time-series identifier
        :return: string representing a dss data type
        """
        # TODO PER-MAX and PER-MIN to DSS/DSSVue  documentation and Java code
        #
        parts = cwms_tsid.split('.')
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
        return dss_type
