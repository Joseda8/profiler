from datetime import datetime


class DatetimeHelper:
    """
    A class for datetime operations.
    """

    @staticmethod
    def current_datetime() -> datetime:
        """
        Get the current datetime.

        Returns:
            str: Current datetime.
        """
        return datetime.now()


    @staticmethod
    def current_datetime_string() -> str:
        """
        Get the current datetime string formatted as "%Y%m%d_%H%M%S".

        Returns:
            str: Current datetime string.
        """
        return datetime.now().strftime("%Y%m%d_%H%M%S")
