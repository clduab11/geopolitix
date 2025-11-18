"""Data transformation utilities."""

from typing import Dict, Optional
import pandas as pd

# ISO 3166-1 alpha-3 to country name mapping
ISO_TO_COUNTRY: Dict[str, str] = {
    "AFG": "Afghanistan",
    "ALB": "Albania",
    "DZA": "Algeria",
    "AGO": "Angola",
    "ARG": "Argentina",
    "ARM": "Armenia",
    "AUS": "Australia",
    "AUT": "Austria",
    "AZE": "Azerbaijan",
    "BHR": "Bahrain",
    "BGD": "Bangladesh",
    "BLR": "Belarus",
    "BEL": "Belgium",
    "BEN": "Benin",
    "BTN": "Bhutan",
    "BOL": "Bolivia",
    "BIH": "Bosnia and Herzegovina",
    "BWA": "Botswana",
    "BRA": "Brazil",
    "BRN": "Brunei",
    "BGR": "Bulgaria",
    "BFA": "Burkina Faso",
    "BDI": "Burundi",
    "KHM": "Cambodia",
    "CMR": "Cameroon",
    "CAN": "Canada",
    "CAF": "Central African Republic",
    "TCD": "Chad",
    "CHL": "Chile",
    "CHN": "China",
    "COL": "Colombia",
    "COD": "Democratic Republic of the Congo",
    "COG": "Republic of the Congo",
    "CRI": "Costa Rica",
    "CIV": "Ivory Coast",
    "HRV": "Croatia",
    "CUB": "Cuba",
    "CYP": "Cyprus",
    "CZE": "Czech Republic",
    "DNK": "Denmark",
    "DJI": "Djibouti",
    "DOM": "Dominican Republic",
    "ECU": "Ecuador",
    "EGY": "Egypt",
    "SLV": "El Salvador",
    "GNQ": "Equatorial Guinea",
    "ERI": "Eritrea",
    "EST": "Estonia",
    "SWZ": "Eswatini",
    "ETH": "Ethiopia",
    "FIN": "Finland",
    "FRA": "France",
    "GAB": "Gabon",
    "GMB": "Gambia",
    "GEO": "Georgia",
    "DEU": "Germany",
    "GHA": "Ghana",
    "GRC": "Greece",
    "GTM": "Guatemala",
    "GIN": "Guinea",
    "GNB": "Guinea-Bissau",
    "GUY": "Guyana",
    "HTI": "Haiti",
    "HND": "Honduras",
    "HUN": "Hungary",
    "ISL": "Iceland",
    "IND": "India",
    "IDN": "Indonesia",
    "IRN": "Iran",
    "IRQ": "Iraq",
    "IRL": "Ireland",
    "ISR": "Israel",
    "ITA": "Italy",
    "JAM": "Jamaica",
    "JPN": "Japan",
    "JOR": "Jordan",
    "KAZ": "Kazakhstan",
    "KEN": "Kenya",
    "KWT": "Kuwait",
    "KGZ": "Kyrgyzstan",
    "LAO": "Laos",
    "LVA": "Latvia",
    "LBN": "Lebanon",
    "LSO": "Lesotho",
    "LBR": "Liberia",
    "LBY": "Libya",
    "LTU": "Lithuania",
    "LUX": "Luxembourg",
    "MDG": "Madagascar",
    "MWI": "Malawi",
    "MYS": "Malaysia",
    "MLI": "Mali",
    "MRT": "Mauritania",
    "MUS": "Mauritius",
    "MEX": "Mexico",
    "MDA": "Moldova",
    "MNG": "Mongolia",
    "MNE": "Montenegro",
    "MAR": "Morocco",
    "MOZ": "Mozambique",
    "MMR": "Myanmar",
    "NAM": "Namibia",
    "NPL": "Nepal",
    "NLD": "Netherlands",
    "NZL": "New Zealand",
    "NIC": "Nicaragua",
    "NER": "Niger",
    "NGA": "Nigeria",
    "PRK": "North Korea",
    "MKD": "North Macedonia",
    "NOR": "Norway",
    "OMN": "Oman",
    "PAK": "Pakistan",
    "PAN": "Panama",
    "PNG": "Papua New Guinea",
    "PRY": "Paraguay",
    "PER": "Peru",
    "PHL": "Philippines",
    "POL": "Poland",
    "PRT": "Portugal",
    "QAT": "Qatar",
    "ROU": "Romania",
    "RUS": "Russia",
    "RWA": "Rwanda",
    "SAU": "Saudi Arabia",
    "SEN": "Senegal",
    "SRB": "Serbia",
    "SLE": "Sierra Leone",
    "SGP": "Singapore",
    "SVK": "Slovakia",
    "SVN": "Slovenia",
    "SOM": "Somalia",
    "ZAF": "South Africa",
    "KOR": "South Korea",
    "SSD": "South Sudan",
    "ESP": "Spain",
    "LKA": "Sri Lanka",
    "SDN": "Sudan",
    "SUR": "Suriname",
    "SWE": "Sweden",
    "CHE": "Switzerland",
    "SYR": "Syria",
    "TWN": "Taiwan",
    "TJK": "Tajikistan",
    "TZA": "Tanzania",
    "THA": "Thailand",
    "TLS": "Timor-Leste",
    "TGO": "Togo",
    "TTO": "Trinidad and Tobago",
    "TUN": "Tunisia",
    "TUR": "Turkey",
    "TKM": "Turkmenistan",
    "UGA": "Uganda",
    "UKR": "Ukraine",
    "ARE": "United Arab Emirates",
    "GBR": "United Kingdom",
    "USA": "United States",
    "URY": "Uruguay",
    "UZB": "Uzbekistan",
    "VEN": "Venezuela",
    "VNM": "Vietnam",
    "YEM": "Yemen",
    "ZMB": "Zambia",
    "ZWE": "Zimbabwe",
}

# Reverse mapping
COUNTRY_TO_ISO: Dict[str, str] = {v: k for k, v in ISO_TO_COUNTRY.items()}


def iso_to_country(iso_code: str) -> str:
    """
    Convert ISO 3166-1 alpha-3 code to country name.

    Args:
        iso_code: Three-letter ISO country code

    Returns:
        Country name or original code if not found
    """
    return ISO_TO_COUNTRY.get(iso_code.upper(), iso_code)


def country_to_iso(country_name: str) -> str:
    """
    Convert country name to ISO 3166-1 alpha-3 code.

    Args:
        country_name: Country name

    Returns:
        ISO code or original name if not found
    """
    # Try exact match first
    if country_name in COUNTRY_TO_ISO:
        return COUNTRY_TO_ISO[country_name]

    # Try normalized match
    normalized = normalize_country_name(country_name)
    for name, code in COUNTRY_TO_ISO.items():
        if normalize_country_name(name) == normalized:
            return code

    return country_name


def normalize_country_name(name: str) -> str:
    """
    Normalize country name for consistent matching.

    Args:
        name: Country name to normalize

    Returns:
        Normalized country name
    """
    # Common name variations
    name_mappings = {
        "united states of america": "United States",
        "usa": "United States",
        "us": "United States",
        "uk": "United Kingdom",
        "great britain": "United Kingdom",
        "russia": "Russia",
        "russian federation": "Russia",
        "south korea": "South Korea",
        "republic of korea": "South Korea",
        "north korea": "North Korea",
        "dprk": "North Korea",
        "iran": "Iran",
        "islamic republic of iran": "Iran",
        "syria": "Syria",
        "syrian arab republic": "Syria",
        "venezuela": "Venezuela",
        "bolivarian republic of venezuela": "Venezuela",
        "vietnam": "Vietnam",
        "viet nam": "Vietnam",
        "congo": "Republic of the Congo",
        "drc": "Democratic Republic of the Congo",
        "dr congo": "Democratic Republic of the Congo",
    }

    normalized = name.lower().strip()
    return name_mappings.get(normalized, name.title())


def calculate_risk_change(
    current: float, previous: float
) -> Dict[str, float]:
    """
    Calculate risk score change metrics.

    Args:
        current: Current risk score
        previous: Previous risk score

    Returns:
        Dictionary with absolute and percentage change
    """
    absolute_change = current - previous
    if previous != 0:
        percentage_change = (absolute_change / previous) * 100
    else:
        percentage_change = 0.0 if current == 0 else 100.0

    return {
        "absolute_change": round(absolute_change, 2),
        "percentage_change": round(percentage_change, 2),
        "direction": "increase" if absolute_change > 0 else "decrease" if absolute_change < 0 else "stable",
    }


def aggregate_risk_scores(
    scores: pd.DataFrame, weight_column: Optional[str] = None
) -> float:
    """
    Aggregate multiple risk scores into a single weighted score.

    Args:
        scores: DataFrame with risk scores
        weight_column: Column name for weights (equal weights if None)

    Returns:
        Weighted average risk score
    """
    if scores.empty:
        return 0.0

    if weight_column and weight_column in scores.columns:
        weights = scores[weight_column]
        values = scores["risk_score"]
        return float((values * weights).sum() / weights.sum())
    else:
        return float(scores["risk_score"].mean())
