from src.util import DatetimeHelper

def set_tag(tag_name: str) -> None:
    """
    Print a tag with the current datetime in seconds since the epoch.

    Args:
        tag_name (str): The name of the tag.
    """
    print(f"measure_label-{tag_name}: {DatetimeHelper.current_datetime(from_the_epoch=True)}")
