import re


SEPATBOLA_KEYWORDS = [
    "LIGA INGGRIS", "LIGA ITALIA", "LIGA JERMAN", "LIGA SPANYOL",
    "LIGA CHAMPION", "BRI SUPER LEAGUE", "FIFA+", "PREMIER LEAGUE",
    "SERIE A", "BUNDESLIGA", "LA LIGA", "CHAMPIONS LEAGUE",
    "EUROPA LEAGUE", "CONFERENCE LEAGUE", "COPA AMERICA", "WORLD CUP",
    "EPL", "UEFA", "LA LIGA", "SERIE A", "BUNDESLIGA",
    "LIGUE 1", "EREDIVISIE", "K-LEAGUE", "AFC",
    "FOOTBALL", "SOCCER",
    "EVENT 0",
    "PEACOCK", "STAR SPORTS SELECT",
    "HUB PREMIER", "NOW SPORTS", "NOW HK PREMIER",
    "ASTRO PREMIER",
    "TNT SPORTS",
    "SKY SPORTS PREMIER",
]

TARUNG_KEYWORDS = [
    "MMA", "UFC", "BOXING", "FIGHT", "WWE", "PFL",
    "ONE CHAMPIONSHIP", "COMBAT", "KICKBOXING",
    "FIGHT SPORTS", "FIGHT TV", "SWERVE COMBAT",
    "UNITED FIGHT", "MMA JUNKIE", "MMA-TV",
    "ADU AYAM",
]

TV_LOKAL_KEYWORDS = [
    "INDONESIA TV", "TVRI DAERAH", "TVRI",
    "HIBURAN", "Ukhuwah Islamiyah",
    "RCTI", "MNCTV", "GTV", "SCTV", "INDOSIAR",
    "TRANS TV", "TRANS 7", "ANTV", "TV ONE", "TVONE",
    "RTV", "MOJI", "METRO TV", "KOMPAS TV",
    "CNN INDONESIA", "CNBC INDONESIA", "INEWS",
    "SINDONEWS", "SEA TODAY", "SINPO TV",
]


def categorize(group_title: str) -> str | None:
    gt_upper = group_title.upper().strip()

    for kw in SEPATBOLA_KEYWORDS:
        if kw.upper() in gt_upper:
            return "sepakbola"

    for kw in TARUNG_KEYWORDS:
        if kw.upper() in gt_upper:
            return "tarung"

    for kw in TV_LOKAL_KEYWORDS:
        if kw.upper() in gt_upper:
            return "tv_lokal"

    return None


def categorize_event(event_name: str, sport: str) -> str | None:
    combined = f"{sport} {event_name}".upper()

    non_football_sports = [
        "BASEBALL", "BASKETBALL", "HOCKEY", "TENNIS", "GOLF",
        "RACING", "MOTOR SPORT", "CRICKET", "RUGBY", "VOLLEYBALL",
        "HANDBALL", "WATER POLO", "CYCLING", "SWIMMING", "ATHLETICS",
        "MLB", "NBA", "WNBA", "NHL", "NFL",
    ]

    for ns in non_football_sports:
        if ns in combined:
            return None

    combat_terms = [
        "UFC", "MMA", "BOXING", "BOX", "WWE", "PFL",
        "ONE CHAMPIONSHIP", "FIGHT", "COMBAT", "KICKBOXING",
        "K-1", "GLORY", "BELLATOR", "CAGE", "BOUT",
        "FIGHT NIGHT", "TITLE FIGHT", "CHAMPIONSHIP FIGHT",
    ]

    for term in combat_terms:
        if term in combined:
            return "tarung"

    football_terms = [
        "VS", "FC", "UNITED", "CITY", "REAL", "BARCELONA", "JUVENTUS",
        "MILAN", "INTER", "BAYERN", "DORTMUND", "LIVERPOOL", "ARSENAL",
        "CHELSEA", "MANCHESTER", "TOTTENHAM", "NEWCASTLE", "ASTON VILLA",
        "WEST HAM", "BRIGHTON", "FULHAM", "WOLVES", "BOURNEMOUTH",
        "BRENTFORD", "EVERTON", "NOTTINGHAM", "CRYSTAL PALACE",
        "SUNDERLAND", "BURNLEY", "LEEDS", "LEICESTER", "SOUTHAMPTON",
        "IPSWICH", "LUTON", "SHEFFIELD",
        "NAPOLI", "ROMA", "LAZIO", "FIORENTINA", "ATALANTA", "BOLOGNA",
        "TORINO", "GENOA", "CAGLIARI", "EMPOLI", "UDINESE", "LECCE",
        "SASSUOLO", "VERONA", "MONZA", "SALERNITANA", "FROSINONE",
        "ATLETICO", "GETAFE", "SEVILLA", "VILLARREAL", "BETIS",
        "VALENCIA", "REAL SOCIEDAD", "ATHLETIC CLUB", "OSASUNA",
        "CELTA VIGO", "GIRONA", "MALLORCA", "CADIZ", "ALAVES",
        "LAS PALMAS", "RAYO VALLECANO", "GRANADA", "OVIEDO",
        "LEVERKUSEN", "LEIPZIG", "STUTTGART", "FRANKFURT",
        "WOLFSBURG", "FREIBURG", "HOFFENHEIM", "MAINZ",
        "AUGSBURG", "BOCHUM", "HEIDENHEIM", "DARMSTADT", "KOELN",
        "HAMBURGER", "HERTHA", "SCHALKE",
        "PSG", "MARSEILLE", "LYON", "MONACO", "LILLE", "NICE",
        "LENS", "RENNES", "STRASBOURG", "NANTES", "TOULOUSE",
        "MONTPELLIER", "LORIENT", "BREST", "ANGERS", "REIMS",
        "AJAX", "PSV", "FEYENOORD", "AZ ALKMAAR", "UTRECHT",
        "TWENTE", "VITESSE", "SPARTA", "HEERENVEEN", "NEC",
        "GO AHEAD EAGLES", "ALMERE", "VOLLENDAM", "EXCELSIOR",
        "CELTIC", "RANGERS", "ABERDEEN", "HIBERNIAN", "HEARTS",
        "DUNDEE", "MOTHERWELL", "ST MIRREN", "ST JOHNSTONE",
        "BENFICA", "PORTO", "SPORTING", "BRAGA",
        "GALATASARAY", "FENERBAHCE", "BESIKTAS",
        "ZENIT", "SPARTAK", "CSKA", "LOKOMOTIV", "DINAMO",
        "SPORTING CP", "FC PORTO", "SL BENFICA",
        "FUTBOL", "FUSSBALL", "SOCCER", "FOOTBALL",
        "SERIE B", "LIGUE 2", "CHAMPIONSHIP", "SERIE A",
        "BUNDESLIGA", "LA LIGA", "LIGUE 1", "EREDIVISIE",
        "PREMIER LEAGUE", "BRASILEIRAO", "BRI SUPER LEAGUE",
        "COPA", "COPPA", "FA CUP", "DFB",
        "INTERNATIONAL FRIEND", "FRIENDLY", "FRIENDLY MATCH",
        "CONMEBOL", "CONCACAF", "EURO QUAL",
        "K-LEAGUE", "AFC", "J-LEAGUE", "A-LEAGUE",
        "LIGA", "EPL", "UEFA",
    ]

    for term in football_terms:
        if term in combined:
            return "sepakbola"

    return None
