from src.const import PREFIX_MEASURE_TAG
from src.util import DatetimeHelper


def set_tag(tag_name: str) -> None:
    """
    Print a tag with the current datetime in seconds since the epoch.

    Args:
        tag_name (str): The name of the tag.
    """
    print(f"{PREFIX_MEASURE_TAG}{tag_name}: {DatetimeHelper.current_datetime(from_the_epoch=True)}")
