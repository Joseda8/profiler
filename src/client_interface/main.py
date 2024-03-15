from src.const import PREFIX_MEASURE_TAG, PREFIX_MEASURE_TAG_FILE_NAME
from src.util import DatetimeHelper


def set_tag(tag_name: str) -> None:
    """
    Print a tag with the current datetime in seconds since the epoch.

    Args:
        tag_name (str): The name of the tag.
    """
    print(f"{PREFIX_MEASURE_TAG}{tag_name}: {DatetimeHelper.current_datetime(from_the_epoch=True)}")

def set_output_filename(filename: str) -> None:
    """
    Print a tag indicating the filename of the output file.

    Args:
        tag_name (str): The name of the tag.
    """
    print(f"{PREFIX_MEASURE_TAG_FILE_NAME}: {filename}")
