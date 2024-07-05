# Dictionary of nicknames per country
nicknames = {
    "costarica": "Ticos",
    "colombia": "Parceros",
    "newzealand": "Kiwis",
    "australia": "Aussies",
    "unitedstates": "Yanks",
    "canada": "Canucks",
    "unitedkingdom": "Brits",
    "japan": "Nipponese",
    "germany": "Krauts",
    "brazil": "Cariocas"
}

def get_nickname_transform_input(country: str) -> str:
    """
    Get nickname based on country and transforming
    the input to match the dictionary keys
    """
    country_lower = country.lower().replace(" ", "")
    return nicknames.get(country_lower, None)

def get_nickname(country: str) -> str:
    """
    Get nickname based on country assuming
    a sanitized input
    """
    return nicknames.get(country, None)
