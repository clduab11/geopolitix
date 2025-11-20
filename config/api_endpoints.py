"""API endpoint definitions for all data sources."""


class APIEndpoints:
    """Central registry of API endpoints for geopolitical data sources."""

    # GDELT Project
    GDELT_BASE_URL = "https://api.gdeltproject.org/api/v2"
    GDELT_DOC_API = f"{GDELT_BASE_URL}/doc/doc"
    GDELT_GEO_API = f"{GDELT_BASE_URL}/geo/geo"
    GDELT_TV_API = f"{GDELT_BASE_URL}/tv/tv"

    # NewsAPI
    NEWSAPI_BASE_URL = "https://newsapi.org/v2"
    NEWSAPI_EVERYTHING = f"{NEWSAPI_BASE_URL}/everything"
    NEWSAPI_TOP_HEADLINES = f"{NEWSAPI_BASE_URL}/top-headlines"

    # World Bank
    WORLDBANK_BASE_URL = "https://api.worldbank.org/v2"
    WORLDBANK_INDICATORS = f"{WORLDBANK_BASE_URL}/country/all/indicator"
    WORLDBANK_COUNTRIES = f"{WORLDBANK_BASE_URL}/country"

    # World Bank Governance Indicators
    WGI_VOICE_ACCOUNTABILITY = "VA.EST"
    WGI_POLITICAL_STABILITY = "PV.EST"
    WGI_GOVERNMENT_EFFECTIVENESS = "GE.EST"
    WGI_REGULATORY_QUALITY = "RQ.EST"
    WGI_RULE_OF_LAW = "RL.EST"
    WGI_CONTROL_OF_CORRUPTION = "CC.EST"

    # ACLED (Armed Conflict Location & Event Data)
    ACLED_BASE_URL = "https://api.acleddata.com/acled/read"

    # Additional Data Sources
    # UN Sanctions
    UN_SANCTIONS_URL = "https://scsanctions.un.org/resources/xml/en/consolidated.xml"

    # Country ISO codes mapping endpoint
    RESTCOUNTRIES_URL = "https://restcountries.com/v3.1/all"

    @classmethod
    def get_worldbank_indicator_url(cls, indicator: str) -> str:
        """Build World Bank indicator API URL."""
        return f"{cls.WORLDBANK_INDICATORS}/{indicator}"

    @classmethod
    def get_gdelt_query_url(cls, query: str, mode: str = "artlist") -> str:
        """Build GDELT query URL."""
        return f"{cls.GDELT_DOC_API}?query={query}&mode={mode}&format=json"
