"""Curated, verified reference data.

Nothing here is fabricated football *performance* data: it is public-record
tournament metadata (hosts, champions, team counts) and country attributes
(confederation, ISO/FIFA codes) used purely for display (flags) and structure.
Match results, scores and goalscorers come entirely from the martj42 dataset.

Sources for the seed facts: FIFA official tournament records / Wikipedia summary
tables (public domain facts). Defunct nations are flagged so the UI can fall back
to a neutral emblem instead of implying a modern flag.
"""
from __future__ import annotations

# (code, full name)
CONFEDERATIONS: list[tuple[str, str]] = [
    ("UEFA", "UEFA (Europe)"),
    ("CONMEBOL", "CONMEBOL (South America)"),
    ("CONCACAF", "CONCACAF (North & Central America)"),
    ("CAF", "CAF (Africa)"),
    ("AFC", "AFC (Asia)"),
    ("OFC", "OFC (Oceania)"),
]

# martj42 team name -> (iso2 for flag CDN | None, FIFA code | None, confederation code, is_defunct)
COUNTRY_META: dict[str, tuple[str | None, str | None, str | None, bool]] = {
    # CONMEBOL
    "Argentina": ("ar", "ARG", "CONMEBOL", False),
    "Brazil": ("br", "BRA", "CONMEBOL", False),
    "Uruguay": ("uy", "URU", "CONMEBOL", False),
    "Chile": ("cl", "CHI", "CONMEBOL", False),
    "Colombia": ("co", "COL", "CONMEBOL", False),
    "Paraguay": ("py", "PAR", "CONMEBOL", False),
    "Peru": ("pe", "PER", "CONMEBOL", False),
    "Ecuador": ("ec", "ECU", "CONMEBOL", False),
    "Bolivia": ("bo", "BOL", "CONMEBOL", False),
    "Venezuela": ("ve", "VEN", "CONMEBOL", False),
    # UEFA
    "Germany": ("de", "GER", "UEFA", False),
    "West Germany": (None, "FRG", "UEFA", True),
    "East Germany": (None, "GDR", "UEFA", True),
    "France": ("fr", "FRA", "UEFA", False),
    "Italy": ("it", "ITA", "UEFA", False),
    "Spain": ("es", "ESP", "UEFA", False),
    "England": ("gb-eng", "ENG", "UEFA", False),
    "Netherlands": ("nl", "NED", "UEFA", False),
    "Portugal": ("pt", "POR", "UEFA", False),
    "Belgium": ("be", "BEL", "UEFA", False),
    "Croatia": ("hr", "CRO", "UEFA", False),
    "Sweden": ("se", "SWE", "UEFA", False),
    "Switzerland": ("ch", "SUI", "UEFA", False),
    "Poland": ("pl", "POL", "UEFA", False),
    "Denmark": ("dk", "DEN", "UEFA", False),
    "Austria": ("at", "AUT", "UEFA", False),
    "Hungary": ("hu", "HUN", "UEFA", False),
    "Czechoslovakia": (None, "TCH", "UEFA", True),
    "Czech Republic": ("cz", "CZE", "UEFA", False),
    "Soviet Union": (None, "URS", "UEFA", True),
    "Russia": ("ru", "RUS", "UEFA", False),
    "Yugoslavia": (None, "YUG", "UEFA", True),
    "Serbia and Montenegro": (None, "SCG", "UEFA", True),
    "Serbia": ("rs", "SRB", "UEFA", False),
    "Republic of Ireland": ("ie", "IRL", "UEFA", False),
    "Northern Ireland": ("gb-nir", "NIR", "UEFA", False),
    "Scotland": ("gb-sct", "SCO", "UEFA", False),
    "Wales": ("gb-wls", "WAL", "UEFA", False),
    "Turkey": ("tr", "TUR", "UEFA", False),
    "Greece": ("gr", "GRE", "UEFA", False),
    "Bulgaria": ("bg", "BUL", "UEFA", False),
    "Romania": ("ro", "ROU", "UEFA", False),
    "Norway": ("no", "NOR", "UEFA", False),
    "Ukraine": ("ua", "UKR", "UEFA", False),
    "Slovenia": ("si", "SVN", "UEFA", False),
    "Slovakia": ("sk", "SVK", "UEFA", False),
    "Bosnia and Herzegovina": ("ba", "BIH", "UEFA", False),
    "Iceland": ("is", "ISL", "UEFA", False),
    "Finland": ("fi", "FIN", "UEFA", False),
    "North Macedonia": ("mk", "MKD", "UEFA", False),
    "Albania": ("al", "ALB", "UEFA", False),
    "Georgia": ("ge", "GEO", "UEFA", False),
    # CONCACAF
    "United States": ("us", "USA", "CONCACAF", False),
    "Mexico": ("mx", "MEX", "CONCACAF", False),
    "Canada": ("ca", "CAN", "CONCACAF", False),
    "Costa Rica": ("cr", "CRC", "CONCACAF", False),
    "Honduras": ("hn", "HON", "CONCACAF", False),
    "Jamaica": ("jm", "JAM", "CONCACAF", False),
    "Panama": ("pa", "PAN", "CONCACAF", False),
    "El Salvador": ("sv", "SLV", "CONCACAF", False),
    "Haiti": ("ht", "HAI", "CONCACAF", False),
    "Trinidad and Tobago": ("tt", "TRI", "CONCACAF", False),
    "Cuba": ("cu", "CUB", "CONCACAF", False),
    # CAF
    "Morocco": ("ma", "MAR", "CAF", False),
    "Senegal": ("sn", "SEN", "CAF", False),
    "Cameroon": ("cm", "CMR", "CAF", False),
    "Nigeria": ("ng", "NGA", "CAF", False),
    "Ghana": ("gh", "GHA", "CAF", False),
    "Algeria": ("dz", "ALG", "CAF", False),
    "Tunisia": ("tn", "TUN", "CAF", False),
    "Egypt": ("eg", "EGY", "CAF", False),
    "South Africa": ("za", "RSA", "CAF", False),
    "Ivory Coast": ("ci", "CIV", "CAF", False),
    "DR Congo": ("cd", "COD", "CAF", False),
    "Zaire": (None, "ZAI", "CAF", True),
    "Angola": ("ao", "ANG", "CAF", False),
    "Togo": ("tg", "TOG", "CAF", False),
    # AFC
    "Japan": ("jp", "JPN", "AFC", False),
    "South Korea": ("kr", "KOR", "AFC", False),
    "North Korea": ("kp", "PRK", "AFC", False),
    "Iran": ("ir", "IRN", "AFC", False),
    "Saudi Arabia": ("sa", "KSA", "AFC", False),
    "Australia": ("au", "AUS", "AFC", False),
    "Qatar": ("qa", "QAT", "AFC", False),
    "China PR": ("cn", "CHN", "AFC", False),
    "Iraq": ("iq", "IRQ", "AFC", False),
    "United Arab Emirates": ("ae", "UAE", "AFC", False),
    "Kuwait": ("kw", "KUW", "AFC", False),
    "Dutch East Indies": (None, "DEI", "AFC", True),
    # OFC
    "New Zealand": ("nz", "NZL", "OFC", False),
}

# Verified men's FIFA World Cup editions (public record).
# teams -> number of finalists; names must match martj42 team names.
MENS_WORLD_CUP_EDITIONS: list[dict] = [
    {"year": 1930, "host": "Uruguay", "champion": "Uruguay", "runner_up": "Argentina", "third": "United States", "teams": 13, "format": "13 teams - 4 groups then knockout"},
    {"year": 1934, "host": "Italy", "champion": "Italy", "runner_up": "Czechoslovakia", "third": "Germany", "teams": 16, "format": "16 teams - single-elimination knockout"},
    {"year": 1938, "host": "France", "champion": "Italy", "runner_up": "Hungary", "third": "Brazil", "teams": 15, "format": "15 teams - single-elimination knockout"},
    {"year": 1950, "host": "Brazil", "champion": "Uruguay", "runner_up": "Brazil", "third": "Sweden", "teams": 13, "format": "13 teams - groups then final round-robin"},
    {"year": 1954, "host": "Switzerland", "champion": "West Germany", "runner_up": "Hungary", "third": "Austria", "teams": 16, "format": "16 teams - groups then knockout"},
    {"year": 1958, "host": "Sweden", "champion": "Brazil", "runner_up": "Sweden", "third": "France", "teams": 16, "format": "16 teams - groups then knockout"},
    {"year": 1962, "host": "Chile", "champion": "Brazil", "runner_up": "Czechoslovakia", "third": "Chile", "teams": 16, "format": "16 teams - groups then knockout"},
    {"year": 1966, "host": "England", "champion": "England", "runner_up": "West Germany", "third": "Portugal", "teams": 16, "format": "16 teams - groups then knockout"},
    {"year": 1970, "host": "Mexico", "champion": "Brazil", "runner_up": "Italy", "third": "West Germany", "teams": 16, "format": "16 teams - groups then knockout"},
    {"year": 1974, "host": "West Germany", "champion": "West Germany", "runner_up": "Netherlands", "third": "Poland", "teams": 16, "format": "16 teams - two group stages"},
    {"year": 1978, "host": "Argentina", "champion": "Argentina", "runner_up": "Netherlands", "third": "Brazil", "teams": 16, "format": "16 teams - two group stages"},
    {"year": 1982, "host": "Spain", "champion": "Italy", "runner_up": "West Germany", "third": "Poland", "teams": 24, "format": "24 teams - two group stages then knockout"},
    {"year": 1986, "host": "Mexico", "champion": "Argentina", "runner_up": "West Germany", "third": "France", "teams": 24, "format": "24 teams - groups then knockout"},
    {"year": 1990, "host": "Italy", "champion": "West Germany", "runner_up": "Argentina", "third": "Italy", "teams": 24, "format": "24 teams - groups then knockout"},
    {"year": 1994, "host": "United States", "champion": "Brazil", "runner_up": "Italy", "third": "Sweden", "teams": 24, "format": "24 teams - groups then knockout"},
    {"year": 1998, "host": "France", "champion": "France", "runner_up": "Brazil", "third": "Croatia", "teams": 32, "format": "32 teams - 8 groups then knockout"},
    {"year": 2002, "host": "South Korea & Japan", "champion": "Brazil", "runner_up": "Germany", "third": "Turkey", "teams": 32, "format": "32 teams - 8 groups then knockout"},
    {"year": 2006, "host": "Germany", "champion": "Italy", "runner_up": "France", "third": "Germany", "teams": 32, "format": "32 teams - 8 groups then knockout"},
    {"year": 2010, "host": "South Africa", "champion": "Spain", "runner_up": "Netherlands", "third": "Germany", "teams": 32, "format": "32 teams - 8 groups then knockout"},
    {"year": 2014, "host": "Brazil", "champion": "Germany", "runner_up": "Argentina", "third": "Netherlands", "teams": 32, "format": "32 teams - 8 groups then knockout"},
    {"year": 2018, "host": "Russia", "champion": "France", "runner_up": "Croatia", "third": "Belgium", "teams": 32, "format": "32 teams - 8 groups then knockout"},
    {"year": 2022, "host": "Qatar", "champion": "Argentina", "runner_up": "France", "third": "Croatia", "teams": 32, "format": "32 teams - 8 groups then knockout"},
    {"year": 2026, "host": "Canada, Mexico & United States", "champion": None, "runner_up": None, "third": None, "teams": 48, "format": "48 teams - 12 groups then knockout", "status": "upcoming"},
]
