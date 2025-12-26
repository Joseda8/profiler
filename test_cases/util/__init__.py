from .file import get_scenario_name, create_directory
from .logger import logger
from .runtime import runtime_flavor_suffix

__all__ = ["DataHandler", "FileWriterCsv", "get_scenario_name", "create_directory", "logger", "runtime_flavor_suffix"]


def __getattr__(name):
    if name == "DataHandler":
        from .data_provider import DataHandler
        return DataHandler
    if name == "FileWriterCsv":
        from .file_writer_csv import FileWriterCsv
        return FileWriterCsv
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
