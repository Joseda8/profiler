import os


def get_scenario_name(file_path: str) -> str:
    """
    Generate a scenario name based on the file path.

    Args:
        file_path (str): The absolute path of the file.

    Returns:
        str: The scenario name.
    """
    # Extract the directory name and filename without extension, then combine them
    scenario_name: str = f"{os.path.splitext(os.path.basename(os.path.dirname(file_path)))[0]}_{os.path.splitext(os.path.basename(file_path))[0]}"
    return scenario_name
