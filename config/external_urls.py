"""External URLs configuration for web scraping and monitoring."""

from typing import Dict, List

# Government websites by country code
GOVERNMENT_URLS: Dict[str, List[str]] = {
    "US": [
        "https://www.state.gov/",
        "https://www.whitehouse.gov/briefing-room/",
    ],
    "UK": [
        "https://www.gov.uk/government/news",
    ],
    "DE": [
        "https://www.bundesregierung.de/breg-en",
    ],
    "FR": [
        "https://www.gouvernement.fr/en",
    ],
    "CN": [
        "http://english.www.gov.cn/",
    ],
    "RU": [
        "http://en.kremlin.ru/",
    ],
}

# Defense ministry URLs by country code
DEFENSE_MINISTRY_URLS: Dict[str, List[str]] = {
    "US": [
        "https://www.defense.gov/News/",
    ],
    "UK": [
        "https://www.gov.uk/government/organisations/ministry-of-defence",
    ],
    "DE": [
        "https://www.bmvg.de/en",
    ],
    "FR": [
        "https://www.defense.gouv.fr/english",
    ],
    "CN": [
        "http://eng.mod.gov.cn/",
    ],
    "RU": [
        "https://eng.mil.ru/en/index.htm",
    ],
}

# Official sanctions tracking sources
SANCTIONS_URLS: List[str] = [
    "https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information",
    "https://www.sanctionsmap.eu/",
    "https://www.un.org/securitycouncil/sanctions/information",
]

# Major think tank URLs for research
THINK_TANK_URLS: List[str] = [
    "https://www.cfr.org/",
    "https://www.csis.org/",
    "https://www.chathamhouse.org/",
    "https://www.brookings.edu/",
    "https://www.rand.org/",
]
