from datetime import datetime
from typing import Union


class DatetimeHelper:
    """
    A class for datetime operations.
    """

    @staticmethod
    def current_datetime(from_the_epoch: bool = False) -> Union[float, datetime]:
        """
        Get the current datetime.

        Args:
            from_the_epoch (bool): If True, returns the current datetime from the epoch.

        Returns:
            Union[float, datetime]: Current datetime as a float timestamp if from_the_epoch is True,
            otherwise returns a datetime object.
        """
        datetime_now = datetime.now()
        return datetime_now.timestamp() if from_the_epoch else datetime_now

    @staticmethod
    def current_datetime_string() -> str:
        """
        Get the current datetime string formatted as "%Y%m%d_%H%M%S".

        Returns:
            str: Current datetime string.
        """
        return datetime.now().strftime("%Y%m%d_%H%M%S")
