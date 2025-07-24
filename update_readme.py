import requests
from datetime import datetime

url = "https://en.wikipedia.org/api/rest_v1/feed/featured/2025/07/24"
today = datetime.utcnow().strftime("%Y/%m/%d")
response = requests.get(f"https://en.wikipedia.org/api/rest_v1/feed/featured/{today}")

if response.status_code == 200:
    data = response.json()
    article = data["tfa"]["normalizedtitle"]
    title_line = f"📖 Today's featured article: [{article}](https://en.wikipedia.org/wiki/{article.replace(' ', '_')})"
else:
    title_line = "⚠️ Could not fetch article."

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

new_readme = readme.split("<!--WIKI:START-->")[0] + \
             "<!--WIKI:START-->\n" + title_line + "\n<!--WIKI:END-->" + \
             readme.split("<!--WIKI:END-->")[1]

with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_readme)
