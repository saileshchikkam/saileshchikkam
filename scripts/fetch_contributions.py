import json, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

USERNAME = sys.argv[1] if len(sys.argv) > 1 else "saileshchikkam"
url = f"https://github.com/users/{USERNAME}/contributions"
r = requests.get(url, headers={"User-Agent": "github-profile-art/1.0"}, timeout=30)
r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")

days = []
for cell in soup.select("td.ContributionCalendar-day, td[data-date]"):
    date = cell.get("data-date")
    if not date:
        continue
    level = int(cell.get("data-level") or 0)
    tip = cell.find("tool-tip")
    label = tip.get_text(" ", strip=True) if tip else ""
    days.append({"date": date, "level": level, "label": label})

if not days:
    raise RuntimeError("GitHub contribution calendar markup was not found.")

payload = {
    "username": USERNAME,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "days": days
}
with open("data/contributions.json", "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)
print(f"Saved {len(days)} contribution cells for {USERNAME}")
