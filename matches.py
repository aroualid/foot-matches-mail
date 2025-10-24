#import requests
#from datetime import date, timedelta
import requests
from datetime import date, timedelta, datetime, timezone, timedelta as td
import locale
from zoneinfo import ZoneInfo  # Python 3.9+
from babel.dates import format_datetime

API_KEY = 'b39c307635184c649c23a7877411b645'

competitions = {
    "🇬🇧 Premier League": 2021,
    "🇪🇺 Champions League": 2001,
    "🇪🇺 Europa League": 2018,
    "🇫🇷 Ligue 1": 2015,
    "🇩🇪 Bundesliga": 2002,
    "🇮🇹 Serie A": 2019,
    "🇪🇸 La Liga": 2014
}

# --- GRANDS CLUBS ---
big_clubs = [
    "Paris Saint-Germain FC", "Olympique de Marseille", "Olympique Lyonnais",
    "Manchester City FC", "Manchester United FC", "Liverpool FC",
    "Arsenal FC", "Chelsea FC", "Tottenham Hotspur FC",
    "FC Barcelona", "Real Madrid CF", "Club Atlético de Madrid",
    "FC Bayern München", "Borussia Dortmund",
    "SSC Napoli", "Juventus FC", "FC Internazionale Milano", "AC Milan",
    "AS Roma"
]

# --- COMPÉTITIONS EUROPÉENNES ---
european_comps = ["Champions League", "Europa League"]

# --- DATES ---
today = date.today()
date_from = today.strftime("%Y-%m-%d")
date_to = (today + timedelta(days=4)).strftime("%Y-%m-%d")  # <-- 4 prochains jours

headers = {"X-Auth-Token": API_KEY}
all_matches = []

# --- RÉCUPÉRATION DES MATCHS ---
for name, comp_id in competitions.items():
    url = f"https://api.football-data.org/v4/competitions/{comp_id}/matches"
    params = {
        "dateFrom": date_from,
        "dateTo": date_to,
        "status": "SCHEDULED"
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    matches = data.get("matches", [])

    filtered = []
    for m in matches:
        home = m["homeTeam"]["name"]
        away = m["awayTeam"]["name"]

        # On garde les matchs européens ou ceux avec un grand club
        if name in european_comps or home in big_clubs or away in big_clubs:
            # Conversion UTC -> Jérusalem & France
            dt_utc = datetime.strptime(m["utcDate"], "%Y-%m-%dT%H:%M:%SZ")
            dt_jerusalem = dt_utc.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("Asia/Jerusalem"))
            dt_fr = dt_utc.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("Europe/Paris"))

            # Format date FR
            dt_str = format_datetime(dt_jerusalem, "EEEE d MMMM 'à' HH'h'mm", locale="fr_FR")

            # --- Attribution du diffuseur ---
            if "Premier League" in name:
                diffuseur = "Canal +"
            elif name in ["🇪🇺 Champions League", "🇪🇺 Europa League"]:
                diffuseur = "Canal +"
            elif name in ["🇩🇪 Bundesliga", "🇪🇸 La Liga"]:
                diffuseur = "BeIN Sports"
            elif name == "🇮🇹 Serie A":
                diffuseur = "DAZN"
            elif name == "🇫🇷 Ligue 1":
                if dt_fr.weekday() == 5 and dt_fr.hour == 17:
                    diffuseur = "Possiblement sur BeIN Sports"
                else:
                    diffuseur = "Ligue 1+"
            else:
                diffuseur = "?"

            # --- Mention spéciale si 2 gros clubs ---
            highlight = ""
            if home in big_clubs and away in big_clubs:
                highlight = " **À NE SURTOUT PAS MANQUER !**"

            filtered.append({
                "competition": name,
                "home": home,
                "away": away,
                "date": dt_str,
                "diffuseur": diffuseur,
                "highlight": highlight
            })

    if filtered:
        all_matches.extend(filtered)

# --- GROUPER PAR COMPÉTITION ---
grouped = {}
for match in all_matches:
    comp = match["competition"]
    if comp not in grouped:
        grouped[comp] = []
    grouped[comp].append(match)

# --- AFFICHAGE final ---
if all_matches:  # Affiche seulement s'il y a des matchs
    print(f"⚽ Matchs des 4 prochains jours :\n")
    for comp, matches in grouped.items():
        print(f"{comp.upper()}")
        for m in matches:
            print(f"- {m['home']} vs {m['away']} - {m['date']} ({m['diffuseur']}){m['highlight']}")
        print()  # ligne vide entre les compétitions
