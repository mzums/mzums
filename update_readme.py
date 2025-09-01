import requests
from datetime import datetime, timezone
import os
from bs4 import BeautifulSoup

def get_featured_article():
    today = datetime.now(timezone.utc).strftime("%Y/%m/%d")
    url = f"https://en.wikipedia.org/api/rest_v1/feed/featured/{today}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            title = data["tfa"]["normalizedtitle"]
            return f"[{title}](https://en.wikipedia.org/wiki/{title.replace(' ', '_')})"
        else:
            return "⚠️ Could not fetch article."
    except Exception as e:
        return f"⚠️ Error: {e}"

def get_xkcd():
    url = "https://xkcd.com/info.0.json"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            title = data['safe_title']
            img_url = data['img']
            alt = data['alt']
            link = f"https://xkcd.com/{data['num']}"
            return f"![{title}]({img_url})\n\n[{title}]({link}) — *{alt}*"
        else:
            return "⚠️ Could not fetch XKCD."
    except Exception as e:
        return f"⚠️ Error: {e}"

def replace_section(content, marker, new_value):
    start = f"<!--{marker}:START-->"
    end = f"<!--{marker}:END-->"
    if start not in content or end not in content:
        print(f"Warning: markers {start} or {end} not found in README.md")
        return content
    pre = content.split(start)[0]
    post = content.split(end)[1]
    return f"{pre}{start}\n{new_value}\n{end}{post}"


with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

def get_did_you_know():
    url = "https://en.wikipedia.org/wiki/Main_Page"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code != 200:
            return f"Request failed with status code: {res.status_code}"
        soup = BeautifulSoup(res.text, "html.parser")
        dyk_div = soup.find("div", id="mp-dyk")
        if not dyk_div:
            return "Did you know section not found"
        facts_list = dyk_div.find("ul").find_all("li", limit=3)
        results = []
        for fact in facts_list:
            fact_text = fact.get_text(" ", strip=True)
            link = fact.find("a")
            if link and link.get("href"):
                href = "https://en.wikipedia.org" + link.get("href")
                fact_text = f"[{fact_text}]({href})"
            results.append(f"- {fact_text}")
        return "\n".join(results)
    except requests.exceptions.RequestException as e:
        return f"Request error: {e}"


def get_pinned_repos():
    username = "mzums"
    token = os.getenv("GH_TOKEN")
    if not token:
        return "GH_TOKEN env var not set"
    query = f"""
    {{
      user(login: "{username}") {{
        pinnedItems(first: 6, types: REPOSITORY) {{
          nodes {{
            ... on Repository {{
              name
              description
              url
            }}
          }}
        }}
      }}
    }}
    """
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post("https://api.github.com/graphql", json={"query": query}, headers=headers)
    if response.status_code != 200:
        return f"GitHub API error {response.status_code}: {response.text}"
    data = response.json()
    repos = data.get("data", {}).get("user", {}).get("pinnedItems", {}).get("nodes", [])
    if not repos:
        return "No pinned repos found"
    result = ""
    for repo in repos:
        name = repo['name']
        url = repo['url']
        desc = f" - {repo['description']}"
        if desc == " - None":
            desc = ""
        result += f"- [{name}]({url}){desc}\n"
    return result.strip()

readme = replace_section(readme, "WIKI", get_featured_article())
readme = replace_section(readme, "XKCD", get_xkcd())
readme = replace_section(readme, "PINNED", get_pinned_repos())
readme = replace_section(readme, "DYK", get_did_you_know())

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)
