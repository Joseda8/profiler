import pandas as pd

def replace_gender(gender: str) -> str:
    """Replace 'female' with 'F' and 'male' with 'M'."""
    if gender == "female":
        return "F"
    elif gender == "male":
        return "M"
    else:
        return "X"

def replace_gender_dataframe(row: pd.Series) -> str:
    """Replace 'female' with 'F' and 'male' with 'M'."""
    if row["gender"] == "female":
        return "F"
    elif row["gender"] == "male":
        return "M"
    else:
        return "X"