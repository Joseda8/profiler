from .main import set_tag, set_output_filename

def __getattr__(name):
    if name == "FileStats":
        # Imports pandas only when requested
        from .process_results import FileStats
        return FileStats
    raise AttributeError(name)
