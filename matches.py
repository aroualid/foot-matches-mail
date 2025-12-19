import os
import requests
from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo
from babel.dates import format_datetime
from email.message import EmailMessage
import smtplib

# --- Variables d'environnement ---
API_KEY = os.getenv("API_KEY")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

# --- Compétitions ---
competitions = {
    "🇬🇧 Premier League": 2021,
    "🇪🇺 Champions League": 2001,
    "🇪🇺 Europa League": 2018,
    "🇫🇷 Ligue 1": 2015,
    "🇩🇪 Bundesliga": 2002,
    "🇮🇹 Serie A": 2019,
    "🇪🇸 La Liga": 2014
}

# --- Grands clubs ---
big_clubs = [
    "Paris Saint-Germain FC", "Olympique de Marseille", "Olympique Lyonnais",
    "Manchester City FC", "Manchester United FC", "Liverpool FC",
    "Arsenal FC", "Chelsea FC", "Tottenham Hotspur FC",
    "FC Barcelona", "Real Madrid CF", "Club Atlético de Madrid",
    "FC Bayern München", "Borussia Dortmund",
    "SSC Napoli", "Juventus FC", "FC Internazionale Milano", "AC Milan",
    "AS Roma"
]

# --- Compétitions européennes ---
european_comps = ["Champions League", "Europa League"]

# --- Dates : aujourd'hui + 4 prochains jours ---
today = date.today()
date_from = today.strftime("%Y-%m-%d")
date_to = (today + timedelta(days=4)).strftime("%Y-%m-%d")

headers = {"X-Auth-Token": API_KEY}
matches_by_competition = {}

for name, comp_id in competitions.items():
    url = f"https://api.football-data.org/v4/competitions/{comp_id}/matches"
    params = {"dateFrom": date_from, "dateTo": date_to, "status": "SCHEDULED"}

    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    matches = data.get("matches", [])
    filtered = []

    for m in matches:
        home = m["homeTeam"]["name"]
        away = m["awayTeam"]["name"]

        if name in european_comps or home in big_clubs or away in big_clubs:
            dt_utc = datetime.strptime(m["utcDate"], "%Y-%m-%dT%H:%M:%SZ")
            dt_jerusalem = dt_utc.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("Asia/Jerusalem"))
            dt_str = format_datetime(dt_jerusalem, "EEEE d MMMM 'à' HH'h'mm", locale="fr_FR")

            # --- Diffuseur ---
            broadcaster = ""
            if "Premier League" in name:
                broadcaster = "Canal+"
            elif name in european_comps:
                broadcaster = "Canal+"
            elif "Bundesliga" in name or "La Liga" in name:
                broadcaster = "BeIN Sports"
            elif "Serie A" in name:
                broadcaster = "DAZN"
            elif "Ligue 1" in name:
                if dt_jerusalem.astimezone(ZoneInfo("Europe/Paris")).weekday() == 5 and dt_jerusalem.hour == 17:
                    broadcaster = "Possiblement sur BeIN Sports"
                else:
                    broadcaster = "Ligue 1+"

            # Mention spéciale si 2 gros clubs
            mention = ""
            if home in big_clubs and away in big_clubs:
                mention = " **À ne surtout pas manquer !**"

            filtered.append(f"{home} vs {away} - {dt_str} ({broadcaster}){mention}")

    if filtered:
        matches_by_competition[name] = filtered

# --- Envoi du mail ---
if matches_by_competition:
    body_lines = ["⚽ Matchs des 4 prochains jours :\n"]
    for comp, games in matches_by_competition.items():
        body_lines.append(f"\n{comp.upper()}\n")
        for g in games:
            body_lines.append(f"• {g}")
    body = "\n".join(body_lines)

    msg = EmailMessage()
    msg["Subject"] = "📅 Matchs à venir"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)

    print("✅ Email envoyé avec succès.")
else:
    print("Aucun match trouvé.") 

