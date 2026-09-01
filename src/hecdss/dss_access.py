from enum import IntEnum


class OpenAccess(IntEnum):
    """OpenAccess is an enumeration of the ways a DSS file can be opened

    The values match the access argument of hec_dss_open_ex in the HEC-DSS C
    library.

    Returns:
        OpenAccess: the access mode
    """

    GENERAL_ACCESS = 0
    """Read or read/write, whichever the file allows.  No error when the file
    does not have write permission.  This is the default."""

    READ_ACCESS = 1
    """Read only; the file will not be written to, and must already exist.
    Several processes may hold the same file open this way at once."""

    MULTI_USER_ACCESS = 2
    """Read/write with full multi-user access.  Usually slow, but necessary when
    more than one process writes to the file at the same time."""

    SINGLE_USER_ADVISORY_ACCESS = 3
    """Read/write with multi-user advisory access.  Errors when the file is read
    only."""

    EXCLUSIVE_ACCESS = 4
    """Exclusive write, used for squeezing.  Errors when exclusive access is not
    available."""
